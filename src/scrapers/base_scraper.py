import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)


class Store:
    """Store data class"""
    def __init__(self, 
                 store_id: str,
                 name: str,
                 city: str,
                 address: str,
                 status: str = "open",
                 phone: Optional[str] = None,
                 hours: Optional[str] = None):
        self.store_id = store_id
        self.name = name
        self.city = city
        self.address = address
        self.status = status  # open, temporarily_closed, permanently_closed
        self.phone = phone
        self.hours = hours
        self.scraped_at = datetime.now()

    def to_dict(self) -> Dict:
        """Convert store to dictionary"""
        return {
            'store_id': self.store_id,
            'name': self.name,
            'city': self.city,
            'address': self.address,
            'status': self.status,
            'phone': self.phone,
            'hours': self.hours,
            'scraped_at': self.scraped_at.isoformat()
        }

    def __repr__(self) -> str:
        return f"Store({self.store_id}, {self.name}, {self.city}, status={self.status})"


class BaseScraper(ABC):
    """Base scraper class for all retailers"""
    
    def __init__(self, timeout: int = 10, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = self._create_session()
        self.logger = logging.getLogger(self.__class__.__name__)

    def _create_session(self) -> requests.Session:
        """Create requests session with retry strategy"""
        session = requests.Session()
        
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS"]
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        return session

    @abstractmethod
    def scrape(self) -> List[Store]:
        """Scrape stores from retailer website
        
        Must be implemented by subclasses
        
        Returns:
            List of Store objects
        """
        pass

    def get_name(self) -> str:
        """Get retailer name"""
        return self.__class__.__name__.replace('Scraper', '')

    def __repr__(self) -> str:
        return f"{self.get_name()}Scraper"
