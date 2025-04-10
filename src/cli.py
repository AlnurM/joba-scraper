import argparse
import json
import sys
import time
from datetime import datetime, timedelta
from loguru import logger

from src.utils.logging_config import setup_logging
from src.scraper import job_scraper
from src.services.scheduler_service import scheduler_service
from src.services.telegram_service import telegram_service


def setup_parser():
    """Set up the argument parser."""
    parser = argparse.ArgumentParser(description='Job Scraper CLI')
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Initialize command
    init_parser = subparsers.add_parser('init', help='Initialize the scraper')
    
    # List websites command
    list_parser = subparsers.add_parser('list', help='List all websites')
    
    # Add website command
    add_parser = subparsers.add_parser('add', help='Add a new website')
    add_parser.add_argument('--name', required=True, help='Website name')
    add_parser.add_argument('--url', required=True, help='Website URL')
    add_parser.add_argument('--selectors', required=True, help='JSON string of selectors')
    add_parser.add_argument('--interval', type=int, default=24, help='Scrape interval in hours')
    add_parser.add_argument('--tags', help='Comma-separated list of tags')
    
    # Scrape command
    scrape_parser = subparsers.add_parser('scrape', help='Scrape a website')
    scrape_parser.add_argument('--name', help='Website name to scrape')
    scrape_parser.add_argument('--url', help='Website URL to scrape')
    scrape_parser.add_argument('--all', action='store_true', help='Scrape all websites')
    
    # Stats command
    stats_parser = subparsers.add_parser('stats', help='Show scraping statistics')
    stats_parser.add_argument('--days', type=int, default=7, help='Number of days to show stats for')
    
    # Test notification command
    notify_parser = subparsers.add_parser('notify', help='Send a test notification')
    notify_parser.add_argument('--message', required=True, help='Message to send')
    
    return parser


def init_command():
    """Initialize the scraper."""
    logger.info("Initializing Job Scraper")
    
    if job_scraper.initialize():
        logger.info("Job Scraper initialized successfully")
        return 0
    else:
        logger.error("Failed to initialize Job Scraper")
        return 1


def list_command():
    """List all websites."""
    if not job_scraper.initialized and not job_scraper.initialize():
        logger.error("Failed to initialize Job Scraper")
        return 1
    
    websites = job_scraper.get_all_websites()
    
    if not websites:
        logger.info("No websites found")
        return 0
    
    logger.info(f"Found {len(websites)} websites:")
    
    for i, website_data in enumerate(websites, 1):
        from src.models.website import Website
        website = Website.from_dict(website_data)
        
        logger.info(f"{i}. {website.name} ({website.url})")
        logger.info(f"   Enabled: {website.enabled}")
        logger.info(f"   Scrape Interval: {website.scrape_interval_hours} hours")
        logger.info(f"   Last Scraped: {website.last_scraped or 'Never'}")
        logger.info(f"   Tags: {', '.join(website.tags) if website.tags else 'None'}")
        logger.info("")
    
    return 0


def add_command(args):
    """Add a new website."""
    if not job_scraper.initialized and not job_scraper.initialize():
        logger.error("Failed to initialize Job Scraper")
        return 1
    
    try:
        # Parse selectors JSON
        selectors = json.loads(args.selectors)
        
        # Parse tags
        tags = args.tags.split(',') if args.tags else []
        
        # Create website data
        website_data = {
            "name": args.name,
            "url": args.url,
            "selectors": selectors,
            "enabled": True,
            "scrape_interval_hours": args.interval,
            "tags": tags,
            "config": {
                "use_javascript": True
            }
        }
        
        # Add website
        website_id = job_scraper.add_website(website_data)
        
        if website_id:
            logger.info(f"Added new website: {args.name} ({args.url})")
        else:
            logger.info(f"Updated existing website: {args.name} ({args.url})")
        
        return 0
        
    except json.JSONDecodeError:
        logger.error("Invalid JSON for selectors")
        return 1
    except Exception as e:
        logger.error(f"Error adding website: {str(e)}")
        return 1


def scrape_command(args):
    """Scrape a website."""
    if not job_scraper.initialized and not job_scraper.initialize():
        logger.error("Failed to initialize Job Scraper")
        return 1
    
    # Initialize the scheduler with the job function
    if not scheduler_service.initialized:
        scheduler_service.initialize(lambda website_data: job_scraper.scrape_website(website_data))
        scheduler_service.start()
    
    try:
        if args.all:
            # Scrape all websites
            websites = job_scraper.get_all_websites()
            
            if not websites:
                logger.info("No websites found to scrape")
                return 0
            
            logger.info(f"Scheduling scraping for {len(websites)} websites")
            
            for i, website_data in enumerate(websites):
                # Add a delay between websites
                delay_seconds = i * 60  # 1 minute between each website
                
                scheduler_service.schedule_website(website_data, delay_seconds)
                
                logger.info(f"Scheduled scraping for {website_data.get('name')} in {delay_seconds} seconds")
            
            # Wait for all jobs to complete
            logger.info("Waiting for all scraping jobs to complete...")
            
            # Sleep for a while to let jobs start
            time.sleep(10)
            
            # Keep checking if there are active jobs
            while scheduler_service.scheduler.get_jobs():
                time.sleep(5)
            
            logger.info("All scraping jobs completed")
            
        elif args.name or args.url:
            # Find the website by name or URL
            websites = job_scraper.get_all_websites()
            
            website_data = None
            for website in websites:
                if args.name and website.get('name') == args.name:
                    website_data = website
                    break
                elif args.url and website.get('url') == args.url:
                    website_data = website
                    break
            
            if not website_data:
                logger.error(f"Website not found: {args.name or args.url}")
                return 1
            
            logger.info(f"Scraping website: {website_data.get('name')} ({website_data.get('url')})")
            
            # Scrape the website directly
            stats = job_scraper.scrape_website(website_data)
            
            if stats and stats.get('success'):
                logger.info(f"Successfully scraped website: {website_data.get('name')}")
                logger.info(f"Found {stats.get('total_jobs_found')} jobs, {stats.get('new_jobs_found')} new")
                return 0
            else:
                logger.error(f"Failed to scrape website: {website_data.get('name')}")
                logger.error(f"Errors: {stats.get('errors', [])}")
                return 1
        else:
            logger.error("Please specify a website name, URL, or use --all")
            return 1
        
        return 0
        
    except Exception as e:
        logger.error(f"Error scraping website: {str(e)}")
        return 1
    finally:
        # Shutdown the scheduler
        scheduler_service.shutdown()


def stats_command(args):
    """Show scraping statistics."""
    if not job_scraper.initialized and not job_scraper.initialize():
        logger.error("Failed to initialize Job Scraper")
        return 1
    
    try:
        # Get stats from the database
        from src.services.database_service import db_service
        
        # Calculate the date range
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=args.days)
        
        # Convert to ISO format strings
        start_date_str = start_date.isoformat()
        end_date_str = end_date.isoformat()
        
        # Query the database for stats
        stats = list(db_service.stats_collection.find({
            "timestamp": {
                "$gte": start_date_str,
                "$lte": end_date_str
            }
        }).sort("timestamp", -1))
        
        if not stats:
            logger.info(f"No statistics found for the last {args.days} days")
            return 0
        
        logger.info(f"Statistics for the last {args.days} days:")
        
        # Group stats by website
        website_stats = {}
        for stat in stats:
            website_name = stat.get('website_name', 'Unknown')
            
            if website_name not in website_stats:
                website_stats[website_name] = {
                    'total_runs': 0,
                    'successful_runs': 0,
                    'total_jobs_found': 0,
                    'new_jobs_found': 0,
                    'total_errors': 0,
                    'avg_duration': 0
                }
            
            website_stats[website_name]['total_runs'] += 1
            
            if stat.get('success'):
                website_stats[website_name]['successful_runs'] += 1
            
            website_stats[website_name]['total_jobs_found'] += stat.get('total_jobs_found', 0)
            website_stats[website_name]['new_jobs_found'] += stat.get('new_jobs_found', 0)
            website_stats[website_name]['total_errors'] += len(stat.get('errors', []))
            
            # Update average duration
            current_avg = website_stats[website_name]['avg_duration']
            current_count = website_stats[website_name]['total_runs']
            new_duration = stat.get('duration_seconds', 0)
            
            website_stats[website_name]['avg_duration'] = (
                (current_avg * (current_count - 1) + new_duration) / current_count
            )
        
        # Print stats for each website
        for website_name, stats in website_stats.items():
            logger.info(f"Website: {website_name}")
            logger.info(f"  Total Runs: {stats['total_runs']}")
            logger.info(f"  Successful Runs: {stats['successful_runs']}")
            logger.info(f"  Success Rate: {stats['successful_runs'] / stats['total_runs'] * 100:.2f}%")
            logger.info(f"  Total Jobs Found: {stats['total_jobs_found']}")
            logger.info(f"  New Jobs Found: {stats['new_jobs_found']}")
            logger.info(f"  Total Errors: {stats['total_errors']}")
            logger.info(f"  Average Duration: {stats['avg_duration']:.2f} seconds")
            logger.info("")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error getting statistics: {str(e)}")
        return 1


def notify_command(args):
    """Send a test notification."""
    try:
        result = telegram_service.send_message_sync(args.message)
        
        if result:
            logger.info("Notification sent successfully")
            return 0
        else:
            logger.error("Failed to send notification")
            return 1
            
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")
        return 1


def main():
    """Main entry point for the CLI."""
    # Setup logging
    setup_logging()
    
    # Set up the argument parser
    parser = setup_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # Execute the appropriate command
    if args.command == 'init':
        return init_command()
    elif args.command == 'list':
        return list_command()
    elif args.command == 'add':
        return add_command(args)
    elif args.command == 'scrape':
        return scrape_command(args)
    elif args.command == 'stats':
        return stats_command(args)
    elif args.command == 'notify':
        return notify_command(args)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())