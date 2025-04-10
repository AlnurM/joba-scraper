from bs4 import BeautifulSoup
import re
from datetime import datetime
from urllib.parse import urljoin
from loguru import logger

from src.models.job import Job


class Parser:
    """Parser for extracting job data from HTML content."""

    @staticmethod
    def extract_jobs(html_content, website_data):
        """
        Extract job data from HTML content based on website configuration.
        
        Args:
            html_content: The HTML content of the page
            website_data: Configuration for extracting data from this website
            
        Returns:
            List of Job objects
        """
        if not html_content:
            logger.warning(f"No HTML content to parse for website: {website_data.get('name', 'Unknown')}")
            return []
            
        try:
            # Parse HTML with BeautifulSoup
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Get selectors from website data
            selectors = website_data.get('selectors', {})
            
            # Get the container selector for job listings
            container_selector = selectors.get('container')
            if not container_selector:
                logger.error(f"No container selector found for website: {website_data.get('name', 'Unknown')}")
                return []
                
            # Find all job containers
            job_containers = soup.select(container_selector)
            logger.info(f"Found {len(job_containers)} job containers for website: {website_data.get('name', 'Unknown')}")
            
            # Extract job data from each container
            jobs = []
            for container in job_containers:
                job = Parser._extract_job_from_container(
                    container, 
                    selectors, 
                    website_data.get('url', ''),
                    website_data.get('_id', '')
                )
                
                if job:
                    jobs.append(job)
            
            logger.info(f"Extracted {len(jobs)} jobs from website: {website_data.get('name', 'Unknown')}")
            return jobs
            
        except Exception as e:
            logger.error(f"Error parsing HTML content for website {website_data.get('name', 'Unknown')}: {str(e)}")
            return []

    @staticmethod
    def _extract_job_from_container(container, selectors, base_url, website_id):
        """
        Extract job data from a single container.
        
        Args:
            container: The BeautifulSoup element containing the job data
            selectors: The selectors for extracting data
            base_url: The base URL of the website
            website_id: The ID of the website
            
        Returns:
            A Job object or None if extraction failed
        """
        try:
            # Extract job data using selectors
            title = Parser._extract_text(container, selectors.get('title'))
            company = Parser._extract_text(container, selectors.get('company'))
            
            # Skip if required fields are missing
            if not title or not company:
                logger.debug("Skipping job: Missing title or company")
                return None
                
            # Extract optional fields
            url = Parser._extract_url(container, selectors.get('url'), base_url)
            location = Parser._extract_text(container, selectors.get('location'))
            description = Parser._extract_text(container, selectors.get('description'))
            salary = Parser._extract_text(container, selectors.get('salary'))
            job_type = Parser._extract_text(container, selectors.get('job_type'))
            posted_date = Parser._extract_text(container, selectors.get('posted_date'))
            
            # Extract external ID if available
            external_id = Parser._extract_text(container, selectors.get('external_id'))
            
            # Create a Job object
            job = Job(
                title=title,
                company=company,
                website_id=website_id,
                url=url,
                location=location,
                description=description,
                salary=salary,
                job_type=job_type,
                posted_date=posted_date,
                external_id=external_id,
                raw_data={
                    'html': str(container)
                }
            )
            
            return job
            
        except Exception as e:
            logger.error(f"Error extracting job from container: {str(e)}")
            return None

    @staticmethod
    def _extract_text(container, selector):
        """
        Extract text from a container using a selector.
        
        Args:
            container: The BeautifulSoup element
            selector: The CSS selector
            
        Returns:
            The extracted text or None if not found
        """
        if not selector:
            return None
            
        try:
            element = container.select_one(selector)
            if not element:
                return None
                
            return element.get_text(strip=True)
        except Exception:
            return None

    @staticmethod
    def _extract_url(container, selector, base_url):
        """
        Extract URL from a container using a selector.
        
        Args:
            container: The BeautifulSoup element
            selector: The CSS selector
            base_url: The base URL of the website
            
        Returns:
            The extracted URL or None if not found
        """
        if not selector:
            return None
            
        try:
            element = container.select_one(selector)
            if not element or not element.has_attr('href'):
                return None
                
            href = element['href']
            # Join with base URL if it's a relative URL
            return urljoin(base_url, href)
        except Exception:
            return None

    @staticmethod
    def parse_date(date_str, format_str=None):
        """
        Parse a date string into a datetime object.
        
        Args:
            date_str: The date string
            format_str: The format string for parsing
            
        Returns:
            A datetime object or None if parsing failed
        """
        if not date_str:
            return None
            
        try:
            if format_str:
                return datetime.strptime(date_str, format_str)
                
            # Try common formats
            formats = [
                '%Y-%m-%d',
                '%d/%m/%Y',
                '%m/%d/%Y',
                '%B %d, %Y',
                '%d %B %Y',
                '%Y-%m-%dT%H:%M:%S',
                '%Y-%m-%d %H:%M:%S'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
                    
            # Try to extract date using regex
            # Match patterns like "2 days ago", "yesterday", etc.
            if re.search(r'(\d+)\s+day', date_str, re.IGNORECASE):
                days = int(re.search(r'(\d+)\s+day', date_str, re.IGNORECASE).group(1))
                return datetime.now() - timedelta(days=days)
                
            if re.search(r'yesterday', date_str, re.IGNORECASE):
                return datetime.now() - timedelta(days=1)
                
            if re.search(r'today', date_str, re.IGNORECASE):
                return datetime.now()
                
            # If all else fails, return None
            return None
            
        except Exception as e:
            logger.error(f"Error parsing date '{date_str}': {str(e)}")
            return None