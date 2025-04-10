import unittest
from bs4 import BeautifulSoup

from src.utils.parser import Parser
from src.models.job import Job


class TestParser(unittest.TestCase):
    """Test cases for the Parser class."""

    def setUp(self):
        """Set up test fixtures."""
        # Sample HTML content for testing
        self.html_content = """
        <div class="job-listings">
            <div class="job-listing">
                <h3 class="job-title"><a href="/jobs/software-engineer">Software Engineer</a></h3>
                <div class="company-name">Example Company</div>
                <div class="job-location">New York, NY</div>
                <div class="job-description">We are looking for a software engineer...</div>
                <div class="job-salary">$100,000 - $120,000</div>
                <div class="job-type">Full-time</div>
                <div class="job-date">2023-01-15</div>
            </div>
            <div class="job-listing">
                <h3 class="job-title"><a href="/jobs/data-scientist">Data Scientist</a></h3>
                <div class="company-name">Another Company</div>
                <div class="job-location">San Francisco, CA</div>
                <div class="job-description">Join our data science team...</div>
                <div class="job-salary">$110,000 - $130,000</div>
                <div class="job-type">Full-time</div>
                <div class="job-date">2023-01-10</div>
            </div>
        </div>
        """
        
        # Sample website data for testing
        self.website_data = {
            "_id": "test_website_id",
            "name": "Test Job Board",
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
            }
        }

    def test_extract_jobs(self):
        """Test extracting jobs from HTML content."""
        jobs = Parser.extract_jobs(self.html_content, self.website_data)
        
        # Check that we extracted the correct number of jobs
        self.assertEqual(len(jobs), 2)
        
        # Check the first job
        job1 = jobs[0]
        self.assertEqual(job1.title, "Software Engineer")
        self.assertEqual(job1.company, "Example Company")
        self.assertEqual(job1.location, "New York, NY")
        self.assertEqual(job1.description, "We are looking for a software engineer...")
        self.assertEqual(job1.salary, "$100,000 - $120,000")
        self.assertEqual(job1.job_type, "Full-time")
        self.assertEqual(job1.posted_date, "2023-01-15")
        self.assertEqual(job1.url, "https://example.com/jobs/software-engineer")
        
        # Check the second job
        job2 = jobs[1]
        self.assertEqual(job2.title, "Data Scientist")
        self.assertEqual(job2.company, "Another Company")
        self.assertEqual(job2.location, "San Francisco, CA")
        self.assertEqual(job2.description, "Join our data science team...")
        self.assertEqual(job2.salary, "$110,000 - $130,000")
        self.assertEqual(job2.job_type, "Full-time")
        self.assertEqual(job2.posted_date, "2023-01-10")
        self.assertEqual(job2.url, "https://example.com/jobs/data-scientist")

    def test_extract_text(self):
        """Test extracting text from HTML elements."""
        soup = BeautifulSoup(self.html_content, 'html.parser')
        container = soup.select_one(".job-listing")
        
        # Test extracting various fields
        title = Parser._extract_text(container, ".job-title")
        company = Parser._extract_text(container, ".company-name")
        location = Parser._extract_text(container, ".job-location")
        
        self.assertEqual(title, "Software Engineer")
        self.assertEqual(company, "Example Company")
        self.assertEqual(location, "New York, NY")
        
        # Test with non-existent selector
        non_existent = Parser._extract_text(container, ".non-existent")
        self.assertIsNone(non_existent)

    def test_extract_url(self):
        """Test extracting URLs from HTML elements."""
        soup = BeautifulSoup(self.html_content, 'html.parser')
        container = soup.select_one(".job-listing")
        
        # Test extracting URL
        url = Parser._extract_url(container, ".job-title a", "https://example.com")
        self.assertEqual(url, "https://example.com/jobs/software-engineer")
        
        # Test with non-existent selector
        non_existent = Parser._extract_url(container, ".non-existent", "https://example.com")
        self.assertIsNone(non_existent)
        
        # Test with element that has no href attribute
        no_href = Parser._extract_url(container, ".company-name", "https://example.com")
        self.assertIsNone(no_href)


if __name__ == '__main__':
    unittest.main()