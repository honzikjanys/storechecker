from typing import List
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .base_scraper import SeleniumScraper, Store
import logging
import time

logger = logging.getLogger(__name__)


class PennyScraper(SeleniumScraper):
    """Scraper for Penny Market Czech Republic using Selenium
    
    Penny uses dynamic JavaScript vyhledávač with autocomplete.
    This scraper uses Selenium to navigate and extract store data.
    """
    
    BASE_URL = "https://www.penny.cz"
    STORES_URL = "https://www.penny.cz/prodejny"

    def scrape(self) -> List[Store]:
        """Scrape Penny Market stores using Selenium
        
        Strategy:
        1. Load the store locator page
        2. Wait for the search/list to load
        3. Extract stores from the rendered HTML
        """
        try:
            driver = self._get_driver()
            logger.info(f"Loading {self.STORES_URL}")
            driver.get(self.STORES_URL)
            
            # Wait for the store list to load
            # Look for the combobox which indicates page is ready
            WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "combobox, [role='combobox']"))
            )
            
            # Wait a bit more for content to render
            time.sleep(3)
            
            # Get the page source after JavaScript rendering
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            
            stores = []
            
            # Try to find store containers - se adjust based on actual HTML
            # Penny might use different approaches for rendering
            # Option 1: Look for specific data attributes or classes that contain store info
            store_items = soup.find_all(['div', 'article', 'li'], 
                                       {'class': lambda x: x and any(cls in (x or '') 
                                       for cls in ['store', 'prodej', 'location', 'item'])})
            
            # Option 2: If no items found, try a broader search
            if not store_items:
                logger.warning("No store items found with primary selectors, trying alternative selectors...")
                # Extract from JSON data or alternative structure
                import json
                scripts = soup.find_all('script', {'type': 'application/json'})
                for script in scripts:
                    try:
                        data = json.loads(script.string)
                        stores = self._extract_from_json(data)
                        if stores:
                            logger.info(f"Extracted {len(stores)} stores from JSON")
                            return stores
                    except (json.JSONDecodeError, TypeError):
                        continue
            else:
                for idx, item in enumerate(store_items, 1):
                    try:
                        store = self._parse_store_item(item, idx)
                        if store:
                            stores.append(store)
                    except Exception as e:
                        logger.warning(f"Failed to parse Penny store item: {e}")
                        continue
            
            logger.info(f"Scraped {len(stores)} Penny stores")
            return stores
            
        except Exception as e:
            logger.error(f"Error scraping Penny stores: {e}", exc_info=True)
            return []
        finally:
            # Note: Don't close driver here to reuse it for efficiency
            # It will be closed on object deletion
            pass

    def _extract_from_json(self, data) -> List[Store]:
        """Try to extract store data from JSON"""
        stores = []
        if isinstance(data, dict):
            # Recursively search for store-like data
            for key, value in data.items():
                if key.lower() in ['stores', 'locations', 'prodejny', 'obchody']:
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
            store_id = item.get('id') or item.get('store_id') or f"penny_{hash(str(item))}"
            name = item.get('name') or item.get('title') or "Unknown"
            city = item.get('city') or item.get('place') or "Unknown"
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
            # Try different selectors
            name = item.find(['h2', 'h3', 'h4', 'strong'], {'class': lambda x: x and 'name' in x.lower()})
            if not name:
                name = item.find(['span', 'div'], {'class': lambda x: x and 'title' in x.lower()})
            
            city = item.find(['span', 'div'], {'class': lambda x: x and 'city' in x.lower()})
            address = item.find(['span', 'p', 'div'], {'class': lambda x: x and 'address' in x.lower()})
            status = item.find(['span', 'div'], {'class': lambda x: x and 'status' in x.lower()})
            
            return Store(
                store_id=f"penny_{idx}",
                name=name.text.strip() if name else "Unknown",
                city=city.text.strip() if city else "Unknown",
                address=address.text.strip() if address else "Unknown",
                status=self._parse_status(status.text if status else "open")
            )
        except Exception as e:
            logger.debug(f"Error parsing store item: {e}")
            return None
    
    def _parse_status(self, status_text: str) -> str:
        """Parse status from text"""
        status_text = status_text.lower()
        if "dočasně" in status_text or "temporary" in status_text:
            return "temporarily_closed"
        elif "zavřeno" in status_text or "closed" in status_text or "permanentně" in status_text:
            return "permanently_closed"
        else:
            return "open"

