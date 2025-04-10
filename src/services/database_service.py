from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from loguru import logger

from src.config import settings


class DatabaseService:
    """Service for interacting with MongoDB database."""

    def __init__(self):
        self.client = None
        self.db = None
        self.jobs_collection = None
        self.websites_collection = None
        self.stats_collection = None

    def connect(self):
        """Connect to MongoDB database."""
        try:
            self.client = MongoClient(settings.MONGODB_URI)
            # Ping the server to check if connection is established
            self.client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
            
            self.db = self.client[settings.DB_NAME]
            self.jobs_collection = self.db[settings.COLLECTION_JOBS]
            self.websites_collection = self.db[settings.COLLECTION_WEBSITES]
            self.stats_collection = self.db[settings.COLLECTION_STATS]
            
            # Create indexes
            self._create_indexes()
            
            return True
        except ConnectionFailure:
            logger.error("Failed to connect to MongoDB")
            return False
        except Exception as e:
            logger.error(f"Error connecting to MongoDB: {str(e)}")
            return False

    def _create_indexes(self):
        """Create necessary indexes for collections."""
        try:
            # Create unique index on job_id and website_id
            self.jobs_collection.create_index([("job_id", 1), ("website_id", 1)], unique=True)
            
            # Create index on website URL
            self.websites_collection.create_index([("url", 1)], unique=True)
            
            logger.info("MongoDB indexes created successfully")
        except OperationFailure as e:
            logger.error(f"Failed to create indexes: {str(e)}")

    def add_website(self, website_data):
        """Add a new website to the database."""
        try:
            result = self.websites_collection.update_one(
                {"url": website_data["url"]},
                {"$set": website_data},
                upsert=True
            )
            
            if result.upserted_id:
                logger.info(f"Added new website: {website_data['url']}")
                return str(result.upserted_id)
            else:
                logger.info(f"Updated existing website: {website_data['url']}")
                return None
        except Exception as e:
            logger.error(f"Error adding website: {str(e)}")
            return None

    def get_all_websites(self):
        """Get all websites from the database."""
        try:
            return list(self.websites_collection.find())
        except Exception as e:
            logger.error(f"Error getting websites: {str(e)}")
            return []

    def save_job(self, job_data):
        """Save a job vacancy to the database."""
        try:
            result = self.jobs_collection.update_one(
                {
                    "job_id": job_data["job_id"],
                    "website_id": job_data["website_id"]
                },
                {"$set": job_data},
                upsert=True
            )
            
            is_new = bool(result.upserted_id)
            if is_new:
                logger.info(f"Added new job: {job_data.get('title', 'Unknown')} from website ID: {job_data['website_id']}")
            else:
                logger.debug(f"Updated existing job: {job_data.get('title', 'Unknown')}")
            
            return is_new
        except Exception as e:
            logger.error(f"Error saving job: {str(e)}")
            return False

    def save_stats(self, stats_data):
        """Save scraping statistics to the database."""
        try:
            self.stats_collection.insert_one(stats_data)
            logger.info(f"Saved scraping stats for run at {stats_data['timestamp']}")
            return True
        except Exception as e:
            logger.error(f"Error saving stats: {str(e)}")
            return False

    def close(self):
        """Close the database connection."""
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed")


# Singleton instance
db_service = DatabaseService()