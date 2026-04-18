from typing import List
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .base_scraper import SeleniumScraper, Store
import logging
import time
import json

logger = logging.getLogger(__name__)


class TescoScraper(SeleniumScraper):
    """Scraper for Tesco Czech Republic using Selenium
    
    Tesco uses iTesco.cz domain for e-commerce with JavaScript vyhledávač.
    This scraper uses Selenium to load and extract store data.
    """
    
    BASE_URL = "https://www.itesco.cz"
    STORES_URL = "https://www.itesco.cz/store-locator"

    def scrape(self) -> List[Store]:
        """Scrape Tesco stores using Selenium
        
        Strategy:
        1. Load the iTesco store locator
        2. Wait for JavaScript to render the store list
        3. Extract stores from the rendered HTML or API data
        """
        try:
            driver = self._get_driver()
            logger.info(f"Loading {self.STORES_URL}")
            driver.get(self.STORES_URL)
            
            # Wait for store list to load
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "[data-store], .store, [role='listitem']"))
            )
            
            time.sleep(3)
            
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            stores = []
            
            # Try JSON first
            scripts = soup.find_all('script', {'type': 'application/json'})
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    extracted = self._extract_from_json(data)
                    if extracted:
                        stores.extend(extracted)
                except (json.JSONDecodeError, TypeError):
                    continue
            
            # Try HTML parsing if no JSON found
            if not stores:
                store_items = soup.find_all(['div', 'article', 'li'],
                                           {'class': lambda x: x and any(cls in (x or '')
                                           for cls in ['store', 'prodej', 'location', 'item'])})
                
                for idx, item in enumerate(store_items, 1):
                    try:
                        store = self._parse_store_item(item, idx)
                        if store:
                            stores.append(store)
                    except Exception as e:
                        logger.debug(f"Failed to parse Tesco store item: {e}")
                        continue
            
            logger.info(f"Scraped {len(stores)} Tesco stores")
            return stores
            
        except Exception as e:
            logger.error(f"Error scraping Tesco stores: {e}", exc_info=True)
            return []

    def _extract_from_json(self, data) -> List[Store]:
        """Try to extract store data from JSON"""
        stores = []
        if isinstance(data, dict):
            for key, value in data.items():
                if key.lower() in ['stores', 'locations', 'prodejny', 'obchody', 'storefinder']:
                    if isinstance(value, list):
                        for item in value:
                            store = self._parse_json_store(item)
                            if store:
                                stores.append(store)
                elif isinstance(value, (dict, list)):
                    stores.extend(self._extract_from_json(value))
        elif isinstance(data, list):
            for item in data:
                store = self._parse_json_store(item)
                if store:
                    stores.append(store)
        return stores
    
    def _parse_json_store(self, item) -> Store:
        """Parse store from JSON object"""
        if not isinstance(item, dict):
            return None
        
        try:
            store_id = item.get('id') or item.get('store_id') or f"tesco_{hash(str(item))}"
            name = item.get('name') or item.get('title') or "Unknown"
            city = item.get('city') or item.get('town') or item.get('place') or "Unknown"
            address = item.get('address') or item.get('street') or "Unknown"
            status = item.get('status') or "open"
            
            return Store(
                store_id=str(store_id),
                name=str(name),
                city=str(city),
                address=str(address),
                status=self._parse_status(str(status))
            )
        except Exception as e:
            logger.debug(f"Failed to parse JSON store: {e}")
            return None
    
    def _parse_store_item(self, item, idx: int) -> Store:
        """Parse individual store item from HTML"""
        try:
            name = item.find(['h2', 'h3', 'h4', 'strong'])
            city = item.find(['span', 'div'], {'class': lambda x: x and 'city' in x.lower()})
            address = item.find(['span', 'p', 'div'], {'class': lambda x: x and 'address' in x.lower()})
            status = item.find(['span', 'div'], {'class': lambda x: x and 'status' in x.lower()})
            
            return Store(
                store_id=f"tesco_{idx}",
                name=name.text.strip() if name else "Unknown",
                city=city.text.strip() if city else "Unknown",
                address=address.text.strip() if address else "Unknown",
                status=self._parse_status(status.text if status else "open")
            )
        except Exception as e:
            logger.debug(f"Error parsing store item: {e}")
            return None
    
    def _parse_status(self, status_text: str) -> str:
        """Parse status from HTML"""
        status_text = status_text.lower()
        if "dočasně" in status_text or "temporary" in status_text:
            return "temporarily_closed"
        elif "zavřeno" in status_text or "closed" in status_text:
            return "permanently_closed"
        else:
            return "open"
