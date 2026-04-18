# StoreChecker 🏪

Monitor store locations and closures from major Czech retail chains with Python.

## Features

- 🛒 **Multi-retailer support**: Tesco, Penny Market, Billa, Albert, Kaufland
- 📊 **Change tracking**: Detect new stores, temporary closures, and permanent closures
- 📧 **Email notifications**: Get notified about store changes
- 📈 **Store statistics**: Keep track of total store counts
- 📅 **Scheduled runs**: Automatic weekly checks with APScheduler
- 💾 **SQLite database**: Persistent storage of store data and history
- 🔄 **Change comparison**: Automatic diff between runs

## Setup

### 1. Clone and install dependencies

```bash
git clone <repo>
cd storechecker
python -m venv venv
source venv/Scripts/activate  # Windows
pip install -r requirements.txt
```

### 2. Configure email notifier

Copy and edit the configuration file:

```bash
cp config.example.py config.py
```

Edit `config.py` with your settings:

```python
# SMTP Configuration (Gmail example)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "your_email@gmail.com"
SMTP_PASSWORD = "your_app_password"  # Use app-specific password for Gmail

# Email recipients
EMAIL_RECIPIENTS = ["your_email@gmail.com", "another@example.com"]

# Scheduling
SCHEDULE_DAY = "monday"
SCHEDULE_TIME = "09:00"
```

**Gmail setup**: If using Gmail, follow these steps:
1. Enable 2-Factor Authentication
2. Create an [App Password](https://myaccount.google.com/apppasswords)
3. Use the generated password in `SMTP_PASSWORD`

### 3. Run the application

**Test run** (execute once):
```bash
python main.py --once
```

**Start scheduler** (runs weekly):
```bash
python main.py --schedule
```

## Output

The application creates:

- `data/stores.db` - SQLite database with store data
- `data/storechecker.log` - Detailed log file
- `data/` - Email reports and artifacts

### Email Report Contents

Each email includes:

1. **Changes section**:
   - ✓ New stores
   - ⏸ Temporarily closed stores
   - ✗ Permanently closed stores
   - ✓ Reopened stores

2. **Summary section**:
   - Store counts by retailer and status
   - Timestamp of the report

## Project Structure

```
storechecker/
├── src/
│   ├── scrapers/          # Web scrapers for each retailer
│   ├── database.py        # SQLite database manager
│   ├── notifier.py        # Email notification system
│   └── scheduler.py       # APScheduler wrapper
├── main.py                # Main application entry point
├── config.example.py      # Configuration template
├── config.py              # Your configuration (gitignore)
├── requirements.txt       # Python dependencies
├── data/                  # Database and log files
└── README.md              # This file
```

## How It Works

### Scraping Process

1. Each scraper fetches the retailer's store list page
2. Parses HTML to extract store information:
   - Store ID and name
   - City and address
   - Operating status
3. Converts to `Store` objects

### Change Detection

1. Saves current stores to SQLite database
2. Compares with previous run
3. Logs detected changes:
   - New stores
   - Status changes (open ↔ closed)
4. Groups changes by type

### Notification

1. Retrieves all changes since last email
2. Generates HTML and plain text email
3. Sends via SMTP

### Scheduling

- Uses APScheduler with cron-like triggers
- Runs weekly on specified day and time
- Background process runs indefinitely

## Customization

### Add a new retailer

1. Create `src/scrapers/myretailer_scraper.py`
2. Extend `BaseScraper`
3. Implement `scrape()` method
4. Add to `SCRAPERS` list in `main.py`

### Change report format

Edit `src/notifier.py`:
- `_create_html_body()` - HTML email format
- `_create_text_body()` - Text email format

### Change detection window

In `src/database.py`, modify `get_changes_since()`:
```python
# Default: 10080 minutes (7 days)
changes = self.db.get_changes_since(minutes=1440)  # 1 day
```

## Troubleshooting

### Scraper returns no stores

The HTML selectors in scrapers are placeholders. You need to inspect the actual retailer websites and update selectors. Use browser DevTools:

1. Visit retailer's store location page
2. Right-click → Inspect
3. Find the correct CSS selectors for store items
4. Update the scraper code

### Email not sending

- Check `config.py` credentials
- For Gmail: Use app-specific password, not regular password
- Ensure SMTP access is enabled
- Check logs in `data/storechecker.log`

### SQLite errors

Delete `data/stores.db` to reset the database:
```bash
rm data/stores.db
python main.py --once
```

## Logging

Logs are written to both:
- Console (INFO level)
- `data/storechecker.log` (INFO level)

Change level in `main.py`:
```python
logging.basicConfig(level=logging.DEBUG)  # More verbose
```

## Performance Tips

- Increase `REQUEST_TIMEOUT` if scrapers timeout
- Reduce `MAX_RETRIES` to fail faster on network errors
- Use `--once` for testing to avoid scheduler overhead

## License

MIT

## Contributing

Feel free to improve the scrapers, add new retailers, or enhance the notification system!
