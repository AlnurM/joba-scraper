#!/usr/bin/env python3
"""
Script to run the application in development mode.
"""

import sys
import os
import argparse
import signal

# Add the parent directory to the path so we can import the application modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.logging_config import setup_logging
from src.scraper import job_scraper
from src.services.scheduler_service import scheduler_service
from loguru import logger


def scrape_website_job(website_data):
    """Job function for scraping a website."""
    return job_scraper.scrape_website(website_data)


def handle_exit(signum, frame):
    """Handle exit signals."""
    logger.info(f"Received signal {signum}. Shutting down...")
    
    # Shutdown scheduler
    scheduler_service.shutdown()
    
    # Shutdown scraper
    job_scraper.shutdown()
    
    logger.info("Shutdown complete. Exiting.")
    sys.exit(0)


def run_dev(no_scheduler=False):
    """Run the application in development mode."""
    # Setup logging
    setup_logging()
    
    logger.info("Starting Job Scraper in development mode")
    
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)
    
    try:
        # Initialize the scraper
        if not job_scraper.initialize():
            logger.error("Failed to initialize Job Scraper. Exiting.")
            return 1
        
        if not no_scheduler:
            # Initialize the scheduler with the job function
            scheduler_service.initialize(scrape_website_job)
            
            # Start the scheduler
            if not scheduler_service.start():
                logger.error("Failed to start scheduler. Exiting.")
                return 1
            
            logger.info("Job Scraper started with scheduler")
        else:
            logger.info("Job Scraper started without scheduler")
        
        # Keep the main thread alive
        while True:
            signal.pause()
            
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received. Shutting down...")
        
        if not no_scheduler:
            scheduler_service.shutdown()
            
        job_scraper.shutdown()
        
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        return 1
        
    return 0


if __name__ == "__main__":
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run the application in development mode')
    parser.add_argument('--no-scheduler', action='store_true', help='Run without the scheduler')
    args = parser.parse_args()
    
    # Run the application
    sys.exit(run_dev(args.no_scheduler))