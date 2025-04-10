from datetime import datetime
from typing import Dict, Any, Optional, List
import hashlib
import json


class Job:
    """Model representing a job vacancy."""

    def __init__(
        self,
        title: str,
        company: str,
        website_id: str,
        url: Optional[str] = None,
        location: Optional[str] = None,
        description: Optional[str] = None,
        salary: Optional[str] = None,
        job_type: Optional[str] = None,
        posted_date: Optional[str] = None,
        raw_data: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        external_id: Optional[str] = None
    ):
        self.title = title
        self.company = company
        self.website_id = website_id
        self.url = url
        self.location = location
        self.description = description
        self.salary = salary
        self.job_type = job_type
        self.posted_date = posted_date
        self.raw_data = raw_data or {}
        self.tags = tags or []
        self.external_id = external_id
        
        # Generate a unique job ID if external_id is not provided
        if not self.external_id:
            self._generate_job_id()
        else:
            self.job_id = self.external_id
        
        # Set creation and update timestamps
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = self.created_at
        
        # Track if this is a new job
        self.is_new = True

    def _generate_job_id(self):
        """Generate a unique job ID based on title, company, and URL."""
        # Create a string with the key fields
        key_string = f"{self.title}|{self.company}|{self.url or ''}|{self.website_id}"
        
        # Generate a hash of the key string
        self.job_id = hashlib.md5(key_string.encode()).hexdigest()

    def to_dict(self) -> Dict[str, Any]:
        """Convert the job to a dictionary for storage."""
        return {
            "job_id": self.job_id,
            "title": self.title,
            "company": self.company,
            "website_id": self.website_id,
            "url": self.url,
            "location": self.location,
            "description": self.description,
            "salary": self.salary,
            "job_type": self.job_type,
            "posted_date": self.posted_date,
            "raw_data": self.raw_data,
            "tags": self.tags,
            "external_id": self.external_id,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Job':
        """Create a Job instance from a dictionary."""
        job = cls(
            title=data.get("title", ""),
            company=data.get("company", ""),
            website_id=data.get("website_id", ""),
            url=data.get("url"),
            location=data.get("location"),
            description=data.get("description"),
            salary=data.get("salary"),
            job_type=data.get("job_type"),
            posted_date=data.get("posted_date"),
            raw_data=data.get("raw_data", {}),
            tags=data.get("tags", []),
            external_id=data.get("external_id")
        )
        
        # Set the job_id directly if it exists in the data
        if "job_id" in data:
            job.job_id = data["job_id"]
        
        # Set timestamps if they exist in the data
        if "created_at" in data:
            job.created_at = data["created_at"]
        
        if "updated_at" in data:
            job.updated_at = data["updated_at"]
        else:
            job.updated_at = datetime.utcnow().isoformat()
        
        # This is not a new job if it's being loaded from the database
        job.is_new = False
        
        return job

    def __str__(self) -> str:
        """String representation of the job."""
        return f"Job(id={self.job_id}, title={self.title}, company={self.company})"

    def __repr__(self) -> str:
        """Representation of the job."""
        return self.__str__()