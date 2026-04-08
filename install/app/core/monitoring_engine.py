"""
Background monitoring engine [REQ-0003, REQ-0022, REQ-0024].

Runs in background thread, periodically checks for namedays and triggers notifications.
"""

import time
from threading import Thread, Event
from typing import List, Optional
from datetime import datetime, timedelta

from app.types import Contact, Notification
from app.utils import get_logger
from app.utils.date_utils import get_today_nameday_date
from app.exceptions import MonitoringException
from app.constants import DEFAULT_CHECK_INTERVAL_MINUTES

logger = get_logger(__name__)


class MonitoringEngine(Thread):
    """
    Background monitoring thread that checks for namedays at configured intervals [REQ-0003, REQ-0022, REQ-0024].
    
    Runs in low-memory mode to avoid consuming resources [REQ-0024].
    Processes nameday matches and triggers notifications [REQ-0004].
    Supports dynamic interval updates without restart [REQ-0003].
    """
    
    def __init__(
        self,
        contact_db,  # ContactDatabaseManager
        nameday_ref,  # NamedayReferenceManager
        notification_queue,  # NotificationQueue
        check_interval_minutes: int = DEFAULT_CHECK_INTERVAL_MINUTES
    ):
        """
        Initialize monitoring engine [REQ-0022].
        
        Args:
            contact_db: ContactDatabaseManager instance
            nameday_ref: NamedayReferenceManager instance
            notification_queue: NotificationQueue instance
            check_interval_minutes: Check interval in minutes [REQ-0003]
        """
        super().__init__(daemon=True)
        self.contact_db = contact_db
        self.nameday_ref = nameday_ref
        self.notification_queue = notification_queue
        self.check_interval = check_interval_minutes * 60  # Convert to seconds
        
        self._stop_event = Event()
        self._running = False
        self._last_check_date = None
    
    def run(self) -> None:
        """
        Main monitoring loop - QThread run method [REQ-0022, REQ-0024].
        
        Periodically checks for namedays at configured intervals.
        Exits gracefully when stop_monitoring() is called.
        """
        try:
            logger.info(f"Monitoring engine started (interval: {self.check_interval} seconds)")
            self._running = True
            
            while not self._stop_event.is_set():
                try:
                    logger.info("Running monitoring cycle [REQ-0022]")
                    
                    # Check for namedays
                    namedays = self.check_namedays()
                    
                    # Queue notifications
                    for nameday in namedays:
                        self.notification_queue.add(nameday)
                    
                    logger.info(f"Monitoring cycle complete: {len(namedays)} notifications queued [REQ-0022]")
                    
                    # Sleep for configured interval
                    logger.info(f"Monitoring sleeping for {self.check_interval} seconds until next cycle [REQ-0022]")
                    self._stop_event.wait(self.check_interval)
                
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {e}", exc_info=True)
                    # Continue running despite errors
                    self._stop_event.wait(60)  # Wait 1 minute before retry
    
        except Exception as e:
            logger.error(f"CRITICAL: Monitoring engine failed during startup: {e}", exc_info=True)
        
        finally:
            self._running = False
            logger.info("Monitoring engine stopped")
    
    def stop_monitoring(self) -> None:
        """
        Stop monitoring gracefully.
        
        Signals the monitoring thread to exit on next iteration.
        """
        logger.info("Stopping monitoring engine...")
        self._stop_event.set()
    
    def check_namedays(self) -> List[Notification]:
        """
        Query databases and find today's namedays [REQ-0004, REQ-0022, REQ-0023].
        
        Returns list of Notification objects for contacts with namedays today.
        Supports multiple same-day namedays [REQ-0004].
        
        Returns:
            List of Notification objects
        
        Raises:
            MonitoringException: If check fails
        """
        try:
            today_date = get_today_nameday_date()  # MM-DD format [REQ-0023]
            
            # Avoid duplicate checks if already checked today
            if self._last_check_date == today_date:
                logger.info(f"Already checked today ({today_date}), skipping full check [REQ-0022]")
                return []
            
            self._last_check_date = today_date
            logger.info(f"Performing full nameday check for {today_date} [REQ-0022]")
            
            # Get names celebrating today [REQ-0004]
            nameday_names = self.nameday_ref.get_names_for_date(today_date)
            
            if not nameday_names:
                logger.debug(f"No namedays found for {today_date}")
                return []
            
            # Find matching contacts [REQ-0004]
            notifications = []
            matched_contacts = self._match_contacts(nameday_names)
            
            for contact in matched_contacts:
                notification = Notification(
                    contact=contact,
                    nameday_date=today_date,
                    timestamp=datetime.now()
                )
                notifications.append(notification)
                logger.info(f"Found nameday: {contact.name} on {today_date}")
            
            logger.info(f"Check complete: {len(notifications)} notifications found")
            return notifications
        
        except Exception as e:
            logger.error(f"Error checking namedays: {e}")
            raise MonitoringException(f"Failed to check namedays: {e}") from e
    
    def set_interval(self, minutes: int) -> None:
        """
        Update check interval. Changes apply without restart [REQ-0003].
        
        Args:
            minutes: New interval in minutes
        """
        from app.constants import MIN_CHECK_INTERVAL, MAX_CHECK_INTERVAL
        
        if not (MIN_CHECK_INTERVAL <= minutes <= MAX_CHECK_INTERVAL):
            logger.warning(f"Invalid interval {minutes}, keeping current {self.check_interval // 60}")
            return
        
        old_interval = self.check_interval
        self.check_interval = minutes * 60
        logger.info(f"Check interval changed: {old_interval // 60} min -> {minutes} min")
    
    def invalidate_check_cache(self) -> None:
        """Invalidate daily check cache to force fresh check on next cycle [REQ-0065].
        
        Called when contacts are added/modified to ensure newly added contacts
        with today's nameday are detected on next monitoring cycle.
        
        This is a no-op if monitoring is not running, but safe to call anytime.
        """
        if self._last_check_date is not None:
            logger.info(f"Invalidating check cache (was: {self._last_check_date}) [REQ-0065]")
            self._last_check_date = None
        else:
            logger.debug("Check cache already invalidated [REQ-0065]")
    
    def is_running(self) -> bool:
        """
        Check if monitoring is currently running.
        
        Returns:
            True if monitoring loop is active
        """
        return self._running and not self._stop_event.is_set()
    
    def _get_today_date(self) -> str:
        """
        Get today's date in MM-DD format [REQ-0023].
        
        Returns:
            Today's date as MM-DD string
        """
        return get_today_nameday_date()
    
    def _match_contacts(self, nameday_names: List[str]) -> List[Contact]:
        """
        Find all contacts with matching namedays [REQ-0004].
        
        Supports multiple same-day namedays [REQ-0004].
        
        Args:
            nameday_names: List of names with namedays today
        
        Returns:
            List of Contact objects with matching namedays
        """
        matched = []
        
        for name in nameday_names:
            # Find contact with this name
            contact = self.contact_db.get_contact_by_name(name)
            if contact and not contact.notification_disabled:
                matched.append(contact)
        
        return matched
