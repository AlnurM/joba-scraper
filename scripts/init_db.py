#!/usr/bin/env python3
"""
Script to initialize the database with sample data.
"""

import sys
import os
import json
from datetime import datetime

# Add the parent directory to the path so we can import the application modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.logging_config import setup_logging
from src.services.database_service import db_service
from src.models.website import Website
from loguru import logger


def init_db():
    """Initialize the database with sample data."""
    # Setup logging
    setup_logging()
    
    logger.info("Initializing database with sample data")
    
    # Connect to the database
    if not db_service.connect():
        logger.error("Failed to connect to database")
        return False
    
    try:
        # Check if there are already websites in the database
        existing_websites = db_service.get_all_websites()
        
        if existing_websites:
            logger.info(f"Database already contains {len(existing_websites)} websites")
            user_input = input("Do you want to add sample websites anyway? (y/n): ")
            
            if user_input.lower() != 'y':
                logger.info("Aborting database initialization")
                return False
        
        # Sample websites
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
            },
            {
                "name": "Tech Jobs Portal",
                "url": "https://techjobs.com/listings",
                "selectors": {
                    "container": ".job-card",
                    "title": ".job-title h2",
                    "company": ".company-name span",
                    "location": ".job-location p",
                    "url": ".job-title a",
                    "description": ".job-description p",
                    "salary": ".compensation",
                    "job_type": ".job-type span",
                    "posted_date": ".posted-date"
                },
                "enabled": True,
                "scrape_interval_hours": 6,
                "tags": ["tech", "it", "sample"],
                "config": {
                    "use_javascript": True
                }
            }
        ]
        
        # Add websites to the database
        for website_data in sample_websites:
            website = Website(**website_data)
            result = db_service.add_website(website.to_dict())
            
            if result:
                logger.info(f"Added new website: {website.name}")
            else:
                logger.info(f"Updated existing website: {website.name}")
        
        logger.success("Database initialized with sample data")
        return True
        
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")
        return False
    finally:
        # Close the database connection
        db_service.close()


if __name__ == "__main__":
    success = init_db()
    sys.exit(0 if success else 1)