import os
import signal
import sys
import time
from loguru import logger

from src.utils.logging_config import setup_logging
from src.scraper import job_scraper
from src.services.scheduler_service import scheduler_service


def handle_exit(signum, frame):
    """Handle exit signals."""
    logger.info(f"Received signal {signum}. Shutting down...")
    
    # Shutdown scheduler
    scheduler_service.shutdown()
    
    # Shutdown scraper
    job_scraper.shutdown()
    
    logger.info("Shutdown complete. Exiting.")
    sys.exit(0)


def scrape_website_job(website_data):
    """Job function for scraping a website."""
    return job_scraper.scrape_website(website_data)


def add_sample_websites():
    """Add sample websites to the database."""
    sample_websites = [
        {
            "name": "Example Job Board",
            "url": "https://example.com/jobs",
            "selectors": {
                "container": ".job-listing",
                "title": ".job-title",
                "company": ".company-name",
                "location": ".job-location",
                "url": ".job-title a",
                "description": ".job-description",
                "salary": ".job-salary",
                "job_type": ".job-type",
                "posted_date": ".job-date"
            },
            "enabled": True,
            "scrape_interval_hours": 24,
            "tags": ["example", "sample"],
            "config": {
                "use_javascript": True
            }
        },
        {
            "name": "Another Job Site",
            "url": "https://anotherjobsite.com/careers",
            "selectors": {
                "container": ".career-item",
                "title": "h3.position-title",
                "company": ".company-info",
                "location": ".location",
                "url": "a.job-link",
                "description": ".job-summary",
                "salary": ".salary-range",
                "job_type": ".employment-type",
                "posted_date": ".post-date"
            },
            "enabled": True,
            "scrape_interval_hours": 12,
            "tags": ["example", "sample"],
            "config": {
                "use_javascript": True
            }
        }
    ]
    
    for website_data in sample_websites:
        job_scraper.add_website(website_data)


def main():
    """Main entry point for the application."""
    # Setup logging
    setup_logging()
    
    logger.info("Starting Job Scraper application")
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)
    
    try:
        # Initialize the scraper
        if not job_scraper.initialize():
            logger.error("Failed to initialize Job Scraper. Exiting.")
            return 1
        
        # Initialize the scheduler with the job function
        scheduler_service.initialize(scrape_website_job)
        
        # Check if we need to add sample websites
        websites = job_scraper.get_all_websites()
        if not websites:
            logger.info("No websites found in database. Adding sample websites.")
            add_sample_websites()
        
        # Start the scheduler
        if not scheduler_service.start():
            logger.error("Failed to start scheduler. Exiting.")
            return 1
        
        logger.info("Job Scraper application started successfully")
        
        # Keep the main thread alive
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Shutting down...")
        scheduler_service.shutdown()
        job_scraper.shutdown()
        
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        return 1
        
    return 0


if __name__ == "__main__":
    sys.exit(main())