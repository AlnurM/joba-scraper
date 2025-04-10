import requests
from requests.exceptions import RequestException
import time
import hashlib
from urllib.parse import urljoin
from loguru import logger

from src.config import settings
from src.services.redis_service import redis_service


class ScraperService:
    """Service for scraping websites using ScraperAPI."""

    def __init__(self):
        self.api_key = settings.SCRAPER_API_KEY
        self.base_url = "http://api.scraperapi.com"
        self.session = requests.Session()
        self.max_retries = settings.MAX_RETRIES
        self.retry_delay = settings.RETRY_DELAY_SECONDS

    def _generate_cache_key(self, url):
        """Generate a cache key for a URL."""
        return f"scraper:url:{hashlib.md5(url.encode()).hexdigest()}"

    def _make_request(self, url, params=None):
        """Make a request to ScraperAPI with retry logic."""
        if not params:
            params = {}
        
        # Add API key to params
        params['api_key'] = self.api_key
        
        # Check rate limiting
        rate_limit_key = "rate_limit:scraper_api"
        if not redis_service.rate_limit(rate_limit_key, limit=60, period=60):
            logger.warning("Rate limit exceeded for ScraperAPI. Waiting...")
            time.sleep(5)  # Wait before retrying
        
        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"Scraping URL: {url} (Attempt {attempt}/{self.max_retries})")
                response = self.session.get(
                    self.base_url,
                    params={**params, 'url': url},
                    timeout=60
                )
                
                if response.status_code == 200:
                    logger.success(f"Successfully scraped URL: {url}")
                    return response
                
                logger.warning(f"Failed to scrape URL: {url}, Status: {response.status_code}, Response: {response.text[:100]}")
                
                if response.status_code == 429:  # Too Many Requests
                    logger.warning(f"Rate limited by ScraperAPI. Waiting {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                elif response.status_code >= 500:  # Server errors
                    logger.warning(f"Server error from ScraperAPI. Waiting {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    # For other errors, wait a shorter time
                    time.sleep(self.retry_delay / 2)
            
            except RequestException as e:
                logger.error(f"Request error for URL {url}: {str(e)}")
                time.sleep(self.retry_delay / 2)
        
        logger.error(f"Failed to scrape URL after {self.max_retries} attempts: {url}")
        return None

    def scrape_website(self, url, use_cache=True, cache_expiry=3600):
        """
        Scrape a website using ScraperAPI.
        
        Args:
            url: The URL to scrape
            use_cache: Whether to use Redis cache
            cache_expiry: Cache expiry time in seconds
            
        Returns:
            The response content or None if failed
        """
        # Check cache first if enabled
        if use_cache:
            cache_key = self._generate_cache_key(url)
            cached_content = redis_service.get_cache(cache_key)
            
            if cached_content:
                logger.info(f"Using cached content for URL: {url}")
                return cached_content
        
        # Make the request
        response = self._make_request(url, params={
            'render': 'true',  # Enable JavaScript rendering
            'country_code': 'us',  # Use US IP addresses
        })
        
        if not response:
            return None
        
        # Try to get the content
        try:
            content = response.text
            
            # Cache the content if enabled
            if use_cache and content:
                cache_key = self._generate_cache_key(url)
                redis_service.set_cache(cache_key, content, expiry=cache_expiry)
            
            return content
        except Exception as e:
            logger.error(f"Error processing response for URL {url}: {str(e)}")
            return None

    def extract_job_data(self, html_content, website_config):
        """
        Extract job data from HTML content based on website configuration.
        This is a placeholder method - in a real implementation, you would use
        a parser like BeautifulSoup or a more advanced solution.
        
        Args:
            html_content: The HTML content of the page
            website_config: Configuration for extracting data from this website
            
        Returns:
            List of extracted job data
        """
        # This is a placeholder. In a real implementation, you would:
        # 1. Use BeautifulSoup or similar to parse the HTML
        # 2. Extract job listings based on the selectors in website_config
        # 3. Return structured job data
        
        logger.info("Extracting job data from HTML content")
        
        # Placeholder for extracted jobs
        # In a real implementation, this would contain actual extracted data
        extracted_jobs = []
        
        # Return the extracted jobs
        return extracted_jobs


# Singleton instance
scraper_service = ScraperService()