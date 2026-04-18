# Scraper Development Guide

## Understanding Scrapers

Each scraper inherits from `BaseScraper` and implements the `scrape()` method. The basic flow is:

1. Make HTTP request to the retailer's store locator page
2. Parse HTML with BeautifulSoup
3. Extract store information from HTML elements
4. Convert to `Store` objects and return

## Placeholder Selectors

The current scrapers use placeholder CSS selectors. You need to inspect the actual websites and update the selectors to match the real HTML structure.

## How to Update Selectors

### Step 1: Find the correct page

Open the retailer's store locator in a browser:
- **Tesco**: https://www.tesco.cz/store-locator
- **Penny**: https://www.penny.cz/najdi-prodejnu
- **Billa**: https://www.billa.cz/cs/obchody
- **Albert**: https://www.albert.cz/lokalita
- **Kaufland**: https://www.kaufland.cz/cs/nakupovani-v-kauflandu/nase-obchody

### Step 2: Inspect the HTML

1. Right-click on a store item → **Inspect** (or press F12)
2. Look at the HTML structure
3. Find the container element for each store
4. Identify CSS selector for: name, city, address, status

Example in DevTools:
```html
<div class="store-item">                    <!-- Container selector -->
  <h3 class="store-name">Tesco Brno</h3>    <!-- name selector -->
  <span class="city">Brno</span>            <!-- city selector -->
  <span class="address">Na Poříčí 1</address> <!-- address selector -->
  <span class="status">Otevřeno</span>      <!-- status selector -->
</div>
```

### Step 3: Update the scraper

Edit the scraper file, e.g., `src/scrapers/tesco_scraper.py`:

```python
def scrape(self) -> List[Store]:
    response = self.session.get(self.STORES_URL, timeout=self.timeout)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # UPDATE THIS LINE with the correct container selector
    store_items = soup.find_all('div', {'class': 'actual-store-class'})
    
    for idx, item in enumerate(store_items, 1):
        store = self._parse_store_item(item, idx)
        if store:
            stores.append(store)
    
    return stores

def _parse_store_item(self, item, idx: int) -> Store:
    # UPDATE THESE with correct selectors for your retailer
    name = item.find('h3', {'class': 'actual-name-class'})
    city = item.find('span', {'class': 'actual-city-class'})
    address = item.find('span', {'class': 'actual-address-class'})
    status = item.find('span', {'class': 'actual-status-class'})
    
    return Store(
        store_id=f"tesco_{idx}",
        name=name.text.strip() if name else "Unknown",
        city=city.text.strip() if city else "Unknown",
        address=address.text.strip() if address else "Unknown",
        status=self._parse_status(status.text if status else "open")
    )
```

## CSS Selectors Cheat Sheet

### Finding selectors in DevTools

- **By class**: `soup.find_all('div', {'class': 'classname'})`
- **By id**: `soup.find_all('div', {'id': 'idname'})`
- **By tag**: `soup.find_all('div')`
- **By attribute**: `soup.find_all('div', {'data-store': 'true'})`

### Useful BeautifulSoup methods

```python
# Find first matching element
item.find('div', {'class': 'name'})

# Find all matching elements
item.find_all('span', {'class': 'city'})

# Find parent element
item.parent

# Get text content
element.text.strip()

# Get attribute value
element.get('href') or element['href']

# More specific selectors (using CSS selectors)
soup.select_one('.store-item > h3')
soup.select('.store-list .store')
```

## Testing Your Changes

### 1. Run a single test

```python
from src.scrapers.tesco_scraper import TescoScraper

scraper = TescoScraper()
stores = scraper.scrape()

print(f"Found {len(stores)} stores")
for store in stores[:3]:
    print(store)
```

### 2. Debug in VS Code

Add a breakpoint in the scraper and use the debugger:

```python
def _parse_store_item(self, item, idx: int) -> Store:
    # Add breakpoint here
    name = item.find('h3', {'class': 'store-name'})
    breakpoint()  # Execution will pause here
    return Store(...)
```

Then run:
```bash
python -m pdb main.py --once
```

## Handling JavaScript-Heavy Websites

Some retailers may load store data with JavaScript. In that case:

1. **Option 1**: Use Selenium (already in requirements.txt)

```python
from selenium import webdriver
from bs4 import BeautifulSoup

def scrape(self) -> List[Store]:
    driver = webdriver.Chrome()
    driver.get(self.STORES_URL)
    # Wait for JavaScript to load
    driver.implicitly_wait(10)
    
    # Get page source after JS rendering
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    # ... rest of parsing
    
    driver.quit()
    return stores
```

2. **Option 2**: Use an API (check Network tab in DevTools)

Many retailers load store data via API. Look for XHR requests in the Network tab and directly call that API instead of scraping HTML.

## Status Parsing

The `_parse_status()` method converts text to standard status values:

```python
def _parse_status(self, status_text: str) -> str:
    status_text = status_text.lower()
    if "dočasně" in status_text or "temporary" in status_text:
        return "temporarily_closed"
    elif "zavřeno" in status_text or "closed" in status_text:
        return "permanently_closed"
    else:
        return "open"
```

Update the Czech keywords if the website uses different terminology.

## Common Issues

### Issue: Scraper returns empty list

**Causes**:
- Wrong CSS selectors
- Page requires JavaScript (use Selenium)
- Website redirects or blocks requests

**Debug**:
```python
response = self.session.get(self.STORES_URL)
print(response.status_code)
print(response.text[:1000])  # Print first 1000 chars
```

### Issue: Elements found but attributes are None

**Cause**: Selector doesn't find the element

**Debug**:
```python
# In _parse_store_item:
print(f"Item HTML: {item}")
print(f"Name element: {name}")
print(f"Name text: {name.text if name else 'NOT FOUND'}")
```

### Issue: Status parsing not working

**Cause**: Website uses different keywords

Check the HTML and update:
```python
def _parse_status(self, status_text: str) -> str:
    text = status_text.lower()
    # Add actual keywords from the website
    if "keyword_from_website" in text:
        return "temporarily_closed"
    # ...
```

## Performance Optimization

### Caching

If a retailer has a stable store structure, cache the parsed data:

```python
import hashlib

def scrape(self) -> List[Store]:
    hash_val = hashlib.md5(response.text.encode()).hexdigest()
    
    if self.cache.get(hash_val):
        return self.cache[hash_val]
    
    stores = self._parse_stores(soup)
    self.cache[hash_val] = stores
    return stores
```

### Async Requests

For faster scraping, use async requests:

```python
import aiohttp

async def scrape(self) -> List[Store]:
    async with aiohttp.ClientSession() as session:
        async with session.get(self.STORES_URL) as response:
            html = await response.text()
            soup = BeautifulSoup(html, 'html.parser')
```

## Contributing

When you successfully update scrapers:

1. Test with `python main.py --once`
2. Verify stores are saved to database: `sqlite3 data/stores.db "SELECT COUNT(*) FROM stores;"`
3. Check logs in `data/storechecker.log`
4. Commit changes and test with `--schedule` mode

Happy scraping! 🎉
