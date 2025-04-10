from datetime import datetime
from typing import Dict, Any, Optional, List


class Website:
    """Model representing a website to scrape for job vacancies."""

    def __init__(
        self,
        name: str,
        url: str,
        selectors: Dict[str, str],
        enabled: bool = True,
        scrape_interval_hours: int = 24,
        last_scraped: Optional[str] = None,
        tags: Optional[List[str]] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.url = url
        self.selectors = selectors
        self.enabled = enabled
        self.scrape_interval_hours = scrape_interval_hours
        self.last_scraped = last_scraped
        self.tags = tags or []
        self.config = config or {}
        
        # Set creation and update timestamps
        self.created_at = datetime.utcnow().isoformat()
        self.updated_at = self.created_at

    def to_dict(self) -> Dict[str, Any]:
        """Convert the website to a dictionary for storage."""
        return {
            "name": self.name,
            "url": self.url,
            "selectors": self.selectors,
            "enabled": self.enabled,
            "scrape_interval_hours": self.scrape_interval_hours,
            "last_scraped": self.last_scraped,
            "tags": self.tags,
            "config": self.config,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Website':
        """Create a Website instance from a dictionary."""
        website = cls(
            name=data.get("name", ""),
            url=data.get("url", ""),
            selectors=data.get("selectors", {}),
            enabled=data.get("enabled", True),
            scrape_interval_hours=data.get("scrape_interval_hours", 24),
            last_scraped=data.get("last_scraped"),
            tags=data.get("tags", []),
            config=data.get("config", {})
        )
        
        # Set timestamps if they exist in the data
        if "created_at" in data:
            website.created_at = data["created_at"]
        
        if "updated_at" in data:
            website.updated_at = data["updated_at"]
        else:
            website.updated_at = datetime.utcnow().isoformat()
        
        return website

    def should_scrape(self) -> bool:
        """
        Determine if the website should be scraped based on the last scrape time
        and the scrape interval.
        """
        if not self.enabled:
            return False
            
        if not self.last_scraped:
            return True
            
        try:
            last_scraped_dt = datetime.fromisoformat(self.last_scraped)
            now = datetime.utcnow()
            
            # Calculate hours since last scrape
            hours_since_last_scrape = (now - last_scraped_dt).total_seconds() / 3600
            
            return hours_since_last_scrape >= self.scrape_interval_hours
        except (ValueError, TypeError):
            # If there's an error parsing the last_scraped timestamp, scrape anyway
            return True

    def update_last_scraped(self):
        """Update the last_scraped timestamp to the current time."""
        self.last_scraped = datetime.utcnow().isoformat()
        self.updated_at = self.last_scraped

    def __str__(self) -> str:
        """String representation of the website."""
        return f"Website(name={self.name}, url={self.url}, enabled={self.enabled})"

    def __repr__(self) -> str:
        """Representation of the website."""
        return self.__str__()