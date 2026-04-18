# 🚀 Quick Start Guide

## 60 seconds to running StoreChecker

### 1️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ Setup Configuration

```bash
cp config.example.py config.py
```

Edit `config.py`:

```python
# Gmail example
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "your_email@gmail.com"
SMTP_PASSWORD = "your_app_password"  # Get from https://myaccount.google.com/apppasswords
EMAIL_RECIPIENTS = ["your_email@gmail.com"]
EMAIL_FROM = "storechecker@example.com"

SCHEDULE_DAY = "monday"  # monday, tuesday, etc.
SCHEDULE_TIME = "09:00"  # 24-hour format
```

### 3️⃣ Test It

```bash
python main.py --once
```

Check for success:
- ✅ No errors in console
- ✅ Test email received (check spam folder!)
- ✅ Database created: `data/stores.db`
- ✅ Logs available: `data/storechecker.log`

### 4️⃣ Run Scheduled

```bash
python main.py --schedule
```

Keep running in the background (or use task scheduler on Windows/cron on Linux).

## Next Steps

- 📖 Read [README.md](README.md) for full documentation
- 🔧 See [SCRAPER_GUIDE.md](SCRAPER_GUIDE.md) to fix the placeholder selectors (important!)
- 🛠️ Check [.instructions.md](.instructions.md) for development guide

## Troubleshooting Quick Links

| Problem | Solution |
|---------|----------|
| Email not working | Check `config.py`, Gmail needs [App Password](https://myaccount.google.com/apppasswords) |
| No stores scraped | Selectors are placeholders - update with real ones from SCRAPER_GUIDE.md |
| Port 587 blocked | Check firewall, or use different SMTP (e.g., port 465) |
| Database error | Delete `data/stores.db` and run again |

## Key Files

- `main.py` - Run this
- `config.py` - Your settings go here
- `src/scrapers/` - Store fetching logic (needs CSS selector updates)
- `data/stores.db` - Your database
- `data/storechecker.log` - Debug logs

## Commands

```bash
# Test run (executes once and sends test email)
python main.py --once

# Run scheduler (keeps running, executes weekly)
python main.py --schedule

# Check database
sqlite3 data/stores.db "SELECT COUNT(*) FROM stores;"

# View logs
tail -f data/storechecker.log
```

That's it! 🎉

---

**Having issues?** Check [README.md](README.md#troubleshooting) or the full [Developer Guide](.instructions.md).
