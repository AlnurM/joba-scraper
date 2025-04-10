from datetime import datetime, timedelta
import time
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.pool import ThreadPoolExecutor
from loguru import logger

from src.config import settings
from src.services.database_service import db_service
from src.services.telegram_service import telegram_service


class SchedulerService:
    """Service for scheduling and managing scraping jobs."""

    def __init__(self):
        self.scheduler = None
        self.initialized = False
        self.job_function = None

    def initialize(self, job_function):
        """
        Initialize the scheduler.
        
        Args:
            job_function: The function to call for each scheduled job
        """
        if self.initialized:
            logger.warning("Scheduler already initialized")
            return True

        self.job_function = job_function
        
        # Configure job stores and executors
        job_stores = {
            'default': MemoryJobStore()
        }
        
        executors = {
            'default': ThreadPoolExecutor(20)
        }
        
        # Create and configure the scheduler
        self.scheduler = BackgroundScheduler(
            jobstores=job_stores,
            executors=executors,
            timezone='UTC'
        )
        
        logger.info("Scheduler initialized")
        self.initialized = True
        return True

    def start(self):
        """Start the scheduler."""
        if not self.initialized:
            logger.error("Cannot start scheduler: Not initialized")
            return False
            
        if self.scheduler.running:
            logger.warning("Scheduler already running")
            return True
            
        try:
            self.scheduler.start()
            logger.info("Scheduler started")
            
            # Schedule the daily job
            self._schedule_daily_job()
            
            # Schedule the initial job to run immediately
            self._schedule_initial_job()
            
            return True
        except Exception as e:
            logger.error(f"Error starting scheduler: {str(e)}")
            return False

    def _schedule_daily_job(self):
        """Schedule the daily job to run at a specific time."""
        # Run daily at 1:00 AM UTC
        self.scheduler.add_job(
            self._run_daily_job,
            CronTrigger(hour=1, minute=0),
            id='daily_job',
            replace_existing=True,
            name='Daily Scraping Job'
        )
        logger.info("Daily job scheduled to run at 1:00 AM UTC")

    def _schedule_initial_job(self):
        """Schedule an initial job to run immediately after startup."""
        self.scheduler.add_job(
            self._run_daily_job,
            'date',
            run_date=datetime.now() + timedelta(seconds=10),
            id='initial_job',
            name='Initial Scraping Job'
        )
        logger.info("Initial job scheduled to run in 10 seconds")

    def _run_daily_job(self):
        """Run the daily job to scrape all websites."""
        logger.info("Starting daily scraping job")
        
        try:
            # Get all enabled websites
            websites = db_service.get_all_websites()
            
            if not websites:
                logger.warning("No websites found to scrape")
                telegram_service.send_message_sync("⚠️ No websites found to scrape")
                return
                
            logger.info(f"Found {len(websites)} websites to check")
            
            # Filter websites that should be scraped based on their last scrape time
            websites_to_scrape = []
            for website_data in websites:
                from src.models.website import Website
                website = Website.from_dict(website_data)
                
                if website.should_scrape():
                    websites_to_scrape.append(website)
            
            if not websites_to_scrape:
                logger.info("No websites need to be scraped at this time")
                return
                
            logger.info(f"Scheduling scraping for {len(websites_to_scrape)} websites")
            
            # Schedule each website to be scraped with a delay between them
            for i, website in enumerate(websites_to_scrape):
                # Add a delay between websites to avoid overwhelming the scraper API
                delay_seconds = i * 60  # 1 minute between each website
                
                self.scheduler.add_job(
                    self.job_function,
                    'date',
                    run_date=datetime.now() + timedelta(seconds=delay_seconds),
                    args=[website.to_dict()],
                    id=f'scrape_{website.url}_{int(time.time())}',
                    name=f'Scrape {website.name}'
                )
                
                logger.info(f"Scheduled scraping for {website.name} in {delay_seconds} seconds")
            
            # Send a notification that the scraping has been scheduled
            message = (
                f"🔄 Scheduled scraping for {len(websites_to_scrape)} websites:\n"
                + "\n".join([f"- {website.name}" for website in websites_to_scrape[:10]])
            )
            
            if len(websites_to_scrape) > 10:
                message += f"\n... and {len(websites_to_scrape) - 10} more"
                
            telegram_service.send_message_sync(message)
            
        except Exception as e:
            error_message = f"Error in daily job: {str(e)}"
            logger.error(error_message)
            telegram_service.send_error_notification_sync(error_message)

    def schedule_website(self, website_data, delay_seconds=0):
        """
        Schedule a specific website to be scraped.
        
        Args:
            website_data: The website data
            delay_seconds: Delay in seconds before running the job
            
        Returns:
            The job ID if successful, None otherwise
        """
        if not self.initialized or not self.scheduler.running:
            logger.error("Cannot schedule website: Scheduler not initialized or not running")
            return None
            
        try:
            from src.models.website import Website
            website = Website.from_dict(website_data)
            
            job_id = f'scrape_{website.url}_{int(time.time())}'
            
            self.scheduler.add_job(
                self.job_function,
                'date',
                run_date=datetime.now() + timedelta(seconds=delay_seconds),
                args=[website_data],
                id=job_id,
                name=f'Scrape {website.name}'
            )
            
            logger.info(f"Scheduled scraping for {website.name} in {delay_seconds} seconds")
            return job_id
        except Exception as e:
            logger.error(f"Error scheduling website: {str(e)}")
            return None

    def shutdown(self):
        """Shutdown the scheduler."""
        if not self.initialized:
            logger.warning("Scheduler not initialized, nothing to shutdown")
            return
            
        if not self.scheduler.running:
            logger.warning("Scheduler not running, nothing to shutdown")
            return
            
        try:
            self.scheduler.shutdown()
            logger.info("Scheduler shutdown successfully")
        except Exception as e:
            logger.error(f"Error shutting down scheduler: {str(e)}")


# Singleton instance
scheduler_service = SchedulerService()