from typing import List
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper, Store
import logging

logger = logging.getLogger(__name__)


class AlbertScraper(BaseScraper):
    """Scraper for Albert (AEON) Czech Republic"""
    
    BASE_URL = "https://www.albert.cz"
    STORES_URL = "https://www.albert.cz/lokalita"

    def scrape(self) -> List[Store]:
        """Scrape Albert stores"""
        try:
            response = self.session.get(
                self.STORES_URL,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            stores = []
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Placeholder selectors - adjust based on actual website
            store_items = soup.find_all('li', {'class': 'store-item'})
            
            for idx, item in enumerate(store_items, 1):
                try:
                    store = self._parse_store_item(item, idx)
                    if store:
                        stores.append(store)
                except Exception as e:
                    logger.warning(f"Failed to parse Albert store item: {e}")
                    continue
            
            logger.info(f"Scraped {len(stores)} Albert stores")
            return stores
            
        except Exception as e:
            logger.error(f"Error scraping Albert stores: {e}")
            return []

    def _parse_store_item(self, item, idx: int) -> Store:
        """Parse individual store item"""
        name = item.find('h4', {'class': 'store-name'})
        city = item.find('span', {'class': 'city-name'})
        address = item.find('span', {'class': 'address-text'})
        status = item.find('span', {'class': 'store-status'})
        
        return Store(
            store_id=f"albert_{idx}",
            name=name.text.strip() if name else "Unknown",
            city=city.text.strip() if city else "Unknown",
            address=address.text.strip() if address else "Unknown",
            status=self._parse_status(status.text if status else "open")
        )
    
    def _parse_status(self, status_text: str) -> str:
        """Parse status from HTML"""
        status_text = status_text.lower()
        if "dočasně" in status_text or "temporary" in status_text:
            return "temporarily_closed"
        elif "zavřeno" in status_text or "closed" in status_text:
            return "permanently_closed"
        else:
            return "open"
