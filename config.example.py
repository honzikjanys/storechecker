# SMTP Configuration
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "your_email@gmail.com"
SMTP_PASSWORD = "your_app_password"  # For Gmail: use app-specific password

# Email recipients
EMAIL_RECIPIENTS = ["your_email@gmail.com"]
EMAIL_FROM = "storechecker@example.com"

# Database
DATABASE_PATH = "./data/stores.db"
LOG_PATH = "./data/logs.log"
REPORTS_PATH = "./data/reports"  # Excel reports directory

# Web scraping
REQUEST_TIMEOUT = 10
MAX_RETRIES = 3

# Scheduling
SCHEDULE_DAY = "monday"  # monday, tuesday, wednesday, thursday, friday, saturday, sunday
SCHEDULE_TIME = "09:00"  # HH:MM format (24h)
