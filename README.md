# Joba Scraper

A Python-based job vacancy scraper that cyclically parses job listings from a list of websites.

## Features

- **Scheduled Scraping**: Automatically scrapes job listings on a configurable schedule
- **Flexible Parsing**: Configurable selectors for different website structures
- **Data Storage**: Stores job data in MongoDB
- **Caching**: Uses Redis for caching and rate limiting
- **Notifications**: Sends notifications about new job listings via Telegram
- **Comprehensive Logging**: Detailed logging with loguru
- **CLI Tool**: Command-line interface for managing the scraper

## Architecture

The project follows a modular architecture with the following components:

### Core Components

- **Scraper**: Main component that orchestrates the scraping process
- **Scheduler**: Manages the scheduling of scraping tasks
- **Parser**: Extracts job data from HTML content
- **Database Service**: Handles interactions with MongoDB
- **Redis Service**: Manages caching and rate limiting
- **Telegram Service**: Sends notifications via Telegram

### Models

- **Job**: Represents a job vacancy
- **Website**: Represents a website to scrape

### Utilities

- **Logging**: Configures logging with loguru
- **CLI**: Command-line interface for managing the scraper

## Setup

### Prerequisites

- Python 3.8+
- MongoDB
- Redis (optional, but recommended)
- Telegram Bot (for notifications)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/joba-scraper.git
   cd joba-scraper
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example`:
   ```
   cp .env.example .env
   ```

5. Edit the `.env` file with your configuration:
   ```
   # API Keys and credentials
   SCRAPER_API_KEY=your_scraper_api_key
   MONGODB_URI=mongodb://username:password@localhost:27017/
   REDIS_HOST=localhost
   REDIS_PORT=6379
   REDIS_PASSWORD=
   TELEGRAM_BOT_TOKEN=your_telegram_bot_token
   TELEGRAM_CHAT_ID=your_chat_id

   # Database settings
   DB_NAME=job_vacancies

   # Scheduler settings
   SCHEDULER_INTERVAL_HOURS=24
   MAX_RETRIES=3
   RETRY_DELAY_SECONDS=300

   # Logging settings
   LOG_LEVEL=INFO
   LOG_FILE=logs/joba_scraper.log
   ```

## Usage

### Running the Scraper

To start the scraper as a daemon:

```
python src/main.py
```

This will initialize the scraper, connect to the database, and start the scheduler.

### Using the CLI

The CLI tool provides various commands for managing the scraper:

#### Initialize the Scraper

```
python src/cli.py init
```

#### List All Websites

```
python src/cli.py list
```

#### Add a New Website

```
python src/cli.py add --name "Example Jobs" --url "https://example.com/jobs" --selectors '{"container": ".job-listing", "title": ".job-title", "company": ".company-name", "location": ".job-location", "url": ".job-title a", "description": ".job-description", "salary": ".job-salary", "job_type": ".job-type", "posted_date": ".job-date"}' --interval 24 --tags "example,tech"
```

#### Scrape a Website

```
python src/cli.py scrape --name "Example Jobs"
```

Or scrape all websites:

```
python src/cli.py scrape --all
```

#### Show Statistics

```
python src/cli.py stats --days 7
```

#### Send a Test Notification

```
python src/cli.py notify --message "Test notification"
```

## Website Configuration

To scrape a website, you need to configure the selectors for extracting job data. The selectors are specified as a JSON object with the following fields:

- `container`: CSS selector for the job listing container
- `title`: CSS selector for the job title
- `company`: CSS selector for the company name
- `location`: CSS selector for the job location
- `url`: CSS selector for the job URL
- `description`: CSS selector for the job description
- `salary`: CSS selector for the job salary
- `job_type`: CSS selector for the job type
- `posted_date`: CSS selector for the job posted date

Example:

```json
{
  "container": ".job-listing",
  "title": ".job-title",
  "company": ".company-name",
  "location": ".job-location",
  "url": ".job-title a",
  "description": ".job-description",
  "salary": ".job-salary",
  "job_type": ".job-type",
  "posted_date": ".job-date"
}
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.