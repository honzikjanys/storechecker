#!/usr/bin/env python3
"""
StoreChecker - Monitor store locations from major Czech retail chains
Supports: Tesco, Penny Market, Billa, Albert, Kaufland
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import List

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent))

from src.scrapers import (
    TescoScraper,
    PennyScraper,
    BillaScraper,
    AlbertScraper,
    KauflandScraper
)
from src.database import StoreDatabase
from src.notifier import EmailNotifier
from src.scheduler import StoreCheckerScheduler

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('./data/storechecker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class StoreChecker:
    """Main application class"""
    
    SCRAPERS = [
        TescoScraper(),
        PennyScraper(),
        BillaScraper(),
        AlbertScraper(),
        KauflandScraper()
    ]
    
    def __init__(self):
        """Initialize StoreChecker"""
        # Try to load config
        try:
            import config
            self.config = config
        except ImportError:
            logger.error(
                "config.py not found! Please copy config.example.py to config.py "
                "and fill in your settings."
            )
            sys.exit(1)
        
        self.db = StoreDatabase(self.config.DATABASE_PATH)
        self.notifier = EmailNotifier(
            smtp_server=self.config.SMTP_SERVER,
            smtp_port=self.config.SMTP_PORT,
            username=self.config.SMTP_USERNAME,
            password=self.config.SMTP_PASSWORD,
            from_email=self.config.EMAIL_FROM
        )
        self.scheduler = StoreCheckerScheduler()

    def check_stores(self) -> None:
        """Execute store check - scrape all retailers and send notifications"""
        logger.info("=" * 60)
        logger.info("Starting store check...")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        
        try:
            # Scrape all retailers
            for scraper in self.SCRAPERS:
                logger.info(f"Scraping {scraper.get_name()}...")
                try:
                    stores = scraper.scrape()
                    if stores:
                        self.db.save_stores(scraper.get_name().upper(), stores)
                    else:
                        logger.warning(f"No stores scraped from {scraper.get_name()}")
                except Exception as e:
                    logger.error(f"Error scraping {scraper.get_name()}: {e}")
                    continue
            
            # Get changes and send notification
            changes = self.db.get_changes_since()
            store_counts = self.db.get_store_count()
            
            # Log summary
            total_changes = sum(len(v) for v in changes.values())
            logger.info(f"Total changes detected: {total_changes}")
            
            if total_changes > 0:
                logger.info(f"  - New stores: {len(changes['new'])}")
                logger.info(f"  - Temporarily closed: {len(changes['temporarily_closed'])}")
                logger.info(f"  - Permanently closed: {len(changes['permanently_closed'])}")
                logger.info(f"  - Reopened: {len(changes['reopened'])}")
            
            # Send email notification
            logger.info("Sending email notification...")
            self.notifier.send_report(
                recipients=self.config.EMAIL_RECIPIENTS,
                changes=changes,
                store_counts=list(store_counts),
                timestamp=start_time
            )
            
        except Exception as e:
            logger.error(f"Error during store check: {e}", exc_info=True)
        
        elapsed = (datetime.now() - start_time).total_seconds()
        logger.info(f"Store check completed in {elapsed:.2f} seconds")
        logger.info("=" * 60)

    def start(self) -> None:
        """Start the scheduler"""
        logger.info("Starting StoreChecker scheduler...")
        
        # Add weekly job
        self.scheduler.add_weekly_job(
            func=self.check_stores,
            day=self.config.SCHEDULE_DAY,
            time=self.config.SCHEDULE_TIME,
            job_id='check_stores'
        )
        
        # Start scheduler
        self.scheduler.start()
        
        # Log scheduled jobs
        jobs = self.scheduler.get_jobs()
        logger.info(f"Scheduled {len(jobs)} job(s):")
        for job in jobs:
            logger.info(f"  - {job.name}: {job.trigger}")
        
        logger.info("StoreChecker is running. Press Ctrl+C to stop.")
        
        # Keep running
        try:
            while True:
                import time
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Stopping StoreChecker...")
            self.scheduler.stop()

    def run_once(self) -> None:
        """Run store check once (for testing)"""
        logger.info("Running store check once...")
        self.check_stores()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='StoreChecker - Monitor store locations from Czech retail chains'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='Run check once and exit (for testing)'
    )
    parser.add_argument(
        '--schedule',
        action='store_true',
        help='Start the scheduler (default: run once)'
    )
    
    args = parser.parse_args()
    
    app = StoreChecker()
    
    if args.schedule:
        app.start()
    else:
        app.run_once()


if __name__ == '__main__':
    main()
