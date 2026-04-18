import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class StoreCheckerScheduler:
    """APScheduler wrapper for StoreChecker"""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()

    def add_weekly_job(self, func: Callable, day: str = 'monday', 
                       time: str = '09:00', job_id: str = 'check_stores') -> bool:
        """Add a weekly job
        
        Args:
            func: Function to call
            day: Day of week (monday-sunday)
            time: Time in HH:MM format
            job_id: ID for this job
        
        Returns:
            True if added successfully
        """
        try:
            # Parse time
            hour, minute = map(int, time.split(':'))
            
            # Map day names to cron values (0=Monday, 6=Sunday)
            day_map = {
                'monday': 0,
                'tuesday': 1,
                'wednesday': 2,
                'thursday': 3,
                'friday': 4,
                'saturday': 5,
                'sunday': 6
            }
            
            cron_day = day_map.get(day.lower())
            if cron_day is None:
                logger.error(f"Invalid day: {day}")
                return False
            
            trigger = CronTrigger(
                day_of_week=cron_day,
                hour=hour,
                minute=minute
            )
            
            self.scheduler.add_job(
                func,
                trigger=trigger,
                id=job_id,
                name=f"Check stores ({day} at {time})",
                replace_existing=True
            )
            
            logger.info(f"Job '{job_id}' scheduled for {day} at {time}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add job: {e}")
            return False

    def start(self) -> None:
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")

    def stop(self) -> None:
        """Stop the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler stopped")

    def is_running(self) -> bool:
        """Check if scheduler is running"""
        return self.scheduler.running

    def get_jobs(self) -> list:
        """Get all scheduled jobs"""
        return self.scheduler.get_jobs()
