import time
from datetime import datetime
import traceback
from loguru import logger

from src.config import settings
from src.services.database_service import db_service
from src.services.redis_service import redis_service
from src.services.scraper_service import scraper_service
from src.services.telegram_service import telegram_service
from src.utils.parser import Parser
from src.models.website import Website


class JobScraper:
    """Main class for scraping job vacancies."""

    def __init__(self):
        self.initialized = False

    def initialize(self):
        """Initialize the scraper and its dependencies."""
        try:
            # Initialize database connection
            if not db_service.connect():
                logger.error("Failed to connect to database")
                return False

            # Initialize Redis connection
            redis_connected = redis_service.connect()
            if not redis_connected:
                logger.warning("Failed to connect to Redis. Continuing without caching.")

            # Initialize Telegram (async)
            telegram_service.send_message_sync("🚀 Job Scraper initialized")

            self.initialized = True
            logger.info("Job Scraper initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing Job Scraper: {str(e)}")
            return False

    def scrape_website(self, website_data):
        """
        Scrape a website for job vacancies.
        
        Args:
            website_data: The website data
            
        Returns:
            A dictionary with statistics about the scraping
        """
        if not self.initialized:
            logger.error("Cannot scrape website: Job Scraper not initialized")
            return None

        start_time = time.time()
        website = Website.from_dict(website_data)
        
        logger.info(f"Starting to scrape website: {website.name} ({website.url})")
        
        stats = {
            "website_id": str(website_data.get("_id", "")),
            "website_name": website.name,
            "website_url": website.url,
            "timestamp": datetime.utcnow().isoformat(),
            "start_time": start_time,
            "end_time": None,
            "duration_seconds": None,
            "total_jobs_found": 0,
            "new_jobs_found": 0,
            "errors": [],
            "success": False
        }
        
        try:
            # Scrape the website
            html_content = scraper_service.scrape_website(website.url)
            
            if not html_content:
                error_msg = f"Failed to scrape website: {website.name}"
                logger.error(error_msg)
                stats["errors"].append(error_msg)
                telegram_service.send_error_notification_sync(error_msg, website.url)
                return stats
            
            # Parse the HTML content
            jobs = Parser.extract_jobs(html_content, website_data)
            
            stats["total_jobs_found"] = len(jobs)
            
            if not jobs:
                logger.warning(f"No jobs found on website: {website.name}")
                
                # Update the last scraped timestamp even if no jobs were found
                website.update_last_scraped()
                db_service.add_website(website.to_dict())
                
                stats["success"] = True
                stats["end_time"] = time.time()
                stats["duration_seconds"] = stats["end_time"] - stats["start_time"]
                
                # Save stats to database
                db_service.save_stats(stats)
                
                return stats
            
            # Save jobs to database
            new_jobs_count = 0
            for job in jobs:
                job_dict = job.to_dict()
                is_new = db_service.save_job(job_dict)
                
                if is_new:
                    new_jobs_count += 1
                    # Send notification for new job
                    telegram_service.send_job_notification_sync(job_dict, website.name)
            
            stats["new_jobs_found"] = new_jobs_count
            
            # Update the last scraped timestamp
            website.update_last_scraped()
            db_service.add_website(website.to_dict())
            
            # Log success
            logger.success(
                f"Successfully scraped website: {website.name}. "
                f"Found {len(jobs)} jobs, {new_jobs_count} new."
            )
            
            # Send summary notification
            if new_jobs_count > 0:
                message = (
                    f"✅ Successfully scraped {website.name}\n"
                    f"Found {len(jobs)} jobs, {new_jobs_count} new."
                )
                telegram_service.send_message_sync(message)
            
            stats["success"] = True
            
        except Exception as e:
            error_msg = f"Error scraping website {website.name}: {str(e)}"
            logger.error(error_msg)
            logger.error(traceback.format_exc())
            stats["errors"].append(error_msg)
            telegram_service.send_error_notification_sync(error_msg, website.url)
        
        finally:
            # Update stats
            stats["end_time"] = time.time()
            stats["duration_seconds"] = stats["end_time"] - stats["start_time"]
            
            # Save stats to database
            db_service.save_stats(stats)
            
            return stats

    def add_website(self, website_data):
        """
        Add a new website to the database.
        
        Args:
            website_data: The website data
            
        Returns:
            The website ID if successful, None otherwise
        """
        if not self.initialized:
            logger.error("Cannot add website: Job Scraper not initialized")
            return None
            
        try:
            # Create a Website object
            website = Website(
                name=website_data.get("name"),
                url=website_data.get("url"),
                selectors=website_data.get("selectors", {}),
                enabled=website_data.get("enabled", True),
                scrape_interval_hours=website_data.get("scrape_interval_hours", 24),
                tags=website_data.get("tags", []),
                config=website_data.get("config", {})
            )
            
            # Save to database
            website_id = db_service.add_website(website.to_dict())
            
            if website_id:
                logger.info(f"Added new website: {website.name} ({website.url})")
                telegram_service.send_message_sync(f"➕ Added new website: {website.name}")
            else:
                logger.info(f"Updated existing website: {website.name} ({website.url})")
                telegram_service.send_message_sync(f"🔄 Updated website: {website.name}")
            
            return website_id
        except Exception as e:
            logger.error(f"Error adding website: {str(e)}")
            return None

    def get_all_websites(self):
        """
        Get all websites from the database.
        
        Returns:
            List of website data
        """
        if not self.initialized:
            logger.error("Cannot get websites: Job Scraper not initialized")
            return []
            
        return db_service.get_all_websites()

    def shutdown(self):
        """Shutdown the scraper and its dependencies."""
        try:
            # Close database connection
            db_service.close()
            
            # Close Redis connection
            redis_service.close()
            
            logger.info("Job Scraper shutdown successfully")
        except Exception as e:
            logger.error(f"Error shutting down Job Scraper: {str(e)}")


# Singleton instance
job_scraper = JobScraper()