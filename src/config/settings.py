import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# API Keys and credentials
SCRAPER_API_KEY = os.getenv("SCRAPER_API_KEY")
MONGODB_URI = os.getenv("MONGODB_URI")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Database settings
DB_NAME = os.getenv("DB_NAME", "job_vacancies")
COLLECTION_JOBS = "jobs"
COLLECTION_WEBSITES = "websites"
COLLECTION_STATS = "stats"

# Scheduler settings
SCHEDULER_INTERVAL_HOURS = int(os.getenv("SCHEDULER_INTERVAL_HOURS", 24))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", 3))
RETRY_DELAY_SECONDS = int(os.getenv("RETRY_DELAY_SECONDS", 300))  # 5 minutes

# Logging settings
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = os.getenv("LOG_FILE", "logs/joba_scraper.log")