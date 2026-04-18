import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

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


class SeleniumScraper(BaseScraper):
    """Base class for JavaScript-heavy scrapers using Selenium"""
    
    def __init__(self, timeout: int = 10, max_retries: int = 3, headless: bool = True):
        super().__init__(timeout, max_retries)
        self.headless = headless
        self.driver = None
    
    def _get_driver(self):
        """Get or create Chrome WebDriver with webdriver-manager"""
        if self.driver is None:
            options = Options()
            if self.headless:
                options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--disable-gpu')
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
            
            try:
                # Use webdriver-manager to automatically download chromedriver
                service = Service(ChromeDriverManager().install())
                self.driver = webdriver.Chrome(service=service, options=options)
                self.logger.info("Chrome WebDriver initialized (auto-managed)")
            except Exception as e:
                self.logger.error(f"Failed to initialize Chrome WebDriver: {e}")
                self.logger.info("Make sure you have Chrome/Chromium installed or: pip install webdriver-manager")
                raise
        
        return self.driver
    
    def _close_driver(self):
        """Close WebDriver"""
        if self.driver is not None:
            try:
                self.driver.quit()
                self.driver = None
                self.logger.debug("WebDriver closed")
            except Exception as e:
                self.logger.warning(f"Error closing WebDriver: {e}")
    
    def wait_for_element(self, by: By, value: str, timeout: int = 10):
        """Wait for element to be present"""
        try:
            driver = self._get_driver()
            wait = WebDriverWait(driver, timeout)
            return wait.until(EC.presence_of_element_located((by, value)))
        except Exception as e:
            self.logger.error(f"Timeout waiting for element {value}: {e}")
            raise
    
    def __del__(self):
        """Cleanup on deletion"""
        self._close_driver()
