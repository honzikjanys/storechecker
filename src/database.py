import sqlite3
import json
import logging
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from pathlib import Path
from src.scrapers.base_scraper import Store

logger = logging.getLogger(__name__)


class StoreDatabase:
    """SQLite database for storing store history and changes"""
    
    def __init__(self, db_path: str = "./data/stores.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize database tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Current stores table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS stores (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    store_id TEXT UNIQUE NOT NULL,
                    retailer TEXT NOT NULL,
                    name TEXT NOT NULL,
                    city TEXT NOT NULL,
                    address TEXT NOT NULL,
                    status TEXT DEFAULT 'open',
                    phone TEXT,
                    hours TEXT,
                    scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Store history table for tracking changes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS store_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    store_id TEXT NOT NULL,
                    retailer TEXT NOT NULL,
                    change_type TEXT NOT NULL,
                    old_status TEXT,
                    new_status TEXT,
                    change_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (store_id) REFERENCES stores(store_id)
                )
            ''')
            
            # Scrape runs table for tracking runs
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS scrape_runs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    retailer TEXT NOT NULL,
                    stores_count INTEGER,
                    run_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    status TEXT DEFAULT 'success'
                )
            ''')
            
            conn.commit()
            logger.info(f"Database initialized at {self.db_path}")

    def save_stores(self, retailer: str, stores: List[Store]) -> None:
        """Save or update stores in database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for store in stores:
                # Check if store exists
                cursor.execute(
                    'SELECT id, status FROM stores WHERE store_id = ?',
                    (store.store_id,)
                )
                existing = cursor.fetchone()
                
                if existing:
                    # Update existing store
                    cursor.execute('''
                        UPDATE stores 
                        SET name = ?, city = ?, address = ?, status = ?,
                            phone = ?, hours = ?, updated_at = ?
                        WHERE store_id = ?
                    ''', (
                        store.name, store.city, store.address, store.status,
                        store.phone, store.hours, datetime.now(), store.store_id
                    ))
                    
                    # Check for status change
                    old_status = existing[1]
                    if old_status != store.status:
                        self._log_change(cursor, store, old_status, store.status)
                else:
                    # Insert new store
                    cursor.execute('''
                        INSERT INTO stores 
                        (store_id, retailer, name, city, address, status, phone, hours)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        store.store_id, retailer, store.name, store.city,
                        store.address, store.status, store.phone, store.hours
                    ))
                    
                    # Log as new store
                    self._log_change(cursor, store, None, store.status, change_type='new')
            
            # Log scrape run
            cursor.execute('''
                INSERT INTO scrape_runs (retailer, stores_count, status)
                VALUES (?, ?, ?)
            ''', (retailer, len(stores), 'success'))
            
            conn.commit()
            logger.info(f"Saved {len(stores)} {retailer} stores")

    def _log_change(self, cursor, store: Store, old_status: Optional[str], 
                   new_status: str, change_type: str = 'status_change') -> None:
        """Log a store change"""
        cursor.execute('''
            INSERT INTO store_history 
            (store_id, retailer, change_type, old_status, new_status)
            VALUES (?, ?, ?, ?, ?)
        ''', (store.store_id, store.store_id.split('_')[0].upper(), 
              change_type, old_status, new_status))

    def get_changes_since(self, minutes: int = 10080) -> Dict[str, List[Dict]]:
        """Get all changes since last N minutes (default: 7 days)
        
        Returns:
            Dictionary with change types as keys
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT * FROM store_history 
                WHERE change_date >= datetime('now', ? || ' minutes')
                ORDER BY change_date DESC
            ''', (-minutes,))
            
            changes = cursor.fetchall()
            
            # Group by change type
            grouped = {
                'new': [],
                'temporarily_closed': [],
                'permanently_closed': [],
                'reopened': []
            }
            
            for change in changes:
                change_dict = dict(change)
                
                if change['change_type'] == 'new':
                    grouped['new'].append(change_dict)
                elif change['new_status'] == 'temporarily_closed':
                    grouped['temporarily_closed'].append(change_dict)
                elif change['new_status'] == 'permanently_closed':
                    grouped['permanently_closed'].append(change_dict)
                elif change['new_status'] == 'open' and change['old_status'] != 'open':
                    grouped['reopened'].append(change_dict)
            
            return grouped

    def get_store_count(self, retailer: Optional[str] = None) -> Dict[str, int]:
        """Get count of stores by retailer and status"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            if retailer:
                cursor.execute('''
                    SELECT status, COUNT(*) FROM stores 
                    WHERE retailer = ?
                    GROUP BY status
                ''', (retailer,))
            else:
                cursor.execute('''
                    SELECT retailer, status, COUNT(*) FROM stores 
                    GROUP BY retailer, status
                ''')
            
            return cursor.fetchall()

    def get_all_stores(self, retailer: Optional[str] = None) -> List[Dict]:
        """Get all stores from database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            if retailer:
                cursor.execute(
                    'SELECT * FROM stores WHERE retailer = ? ORDER BY city',
                    (retailer,)
                )
            else:
                cursor.execute('SELECT * FROM stores ORDER BY retailer, city')
            
            return [dict(row) for row in cursor.fetchall()]
