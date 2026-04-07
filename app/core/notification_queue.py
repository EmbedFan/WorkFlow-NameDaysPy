"""
Notification queue for managing pending notifications [REQ-0004, REQ-0009].

Thread-safe queue for storing and processing notifications.
"""

from typing import List, Optional
from collections import deque
from threading import Lock

from app.types import Notification
from app.utils import get_logger

logger = get_logger(__name__)


class NotificationQueue:
    """
    Thread-safe queue for managing pending notifications [REQ-0004, REQ-0009].
    
    Stores notifications in FIFO order and provides thread-safe access.
    Supports deduplication to avoid duplicate notifications.
    """
    
    def __init__(self, max_size: int = 100):
        """
        Initialize notification queue.
        
        Args:
            max_size: Maximum queue size
        """
        self.max_size = max_size
        self._queue: deque = deque(maxlen=max_size)
        self._lock = Lock()
        self._displayed_today = set()  # Track displayed notifications
    
    def add(self, notification: Notification) -> bool:
        """
        Add notification to queue [REQ-0004, REQ-0009].
        
        Thread-safe. Prevents duplicate notifications for same contact on same date.
        
        Args:
            notification: Notification object to add
        
        Returns:
            True if added, False if duplicate or queue full
        """
        # Check for duplicates
        notification_key = (notification.contact.name, notification.nameday_date)
        
        with self._lock:
            # Check if already in queue
            for notif in self._queue:
                if (notif.contact.name, notif.nameday_date) == notification_key:
                    logger.debug(f"Duplicate notification prevented: {notification.contact.name}")
                    return False
            
            # Add to queue
            try:
                self._queue.append(notification)
                logger.info(f"Notification added to queue: {notification.contact.name}")
                return True
            except Exception as e:
                logger.error(f"Failed to add notification: {e}")
                return False
    
    def get_next(self) -> Optional[Notification]:
        """
        Get next notification from queue (FIFO).
        
        Thread-safe.
        
        Returns:
            Next Notification, or None if queue is empty
        """
        with self._lock:
            try:
                if len(self._queue) > 0:
                    notification = self._queue.popleft()
                    logger.info(f"Notification retrieved from queue: {notification.contact.name}")
                    return notification
                return None
            except Exception as e:
                logger.error(f"Error getting notification: {e}")
                return None
    
    def peek_next(self) -> Optional[Notification]:
        """
        Peek at next notification without removing from queue.
        
        Thread-safe.
        
        Returns:
            Next Notification, or None if queue is empty
        """
        with self._lock:
            try:
                if len(self._queue) > 0:
                    return self._queue[0]
                return None
            except Exception:
                return None
    
    def get_all(self) -> List[Notification]:
        """
        Get all notifications currently in queue.
        
        Returns a copy; does not modify queue.
        
        Returns:
            List of all pending notifications
        """
        with self._lock:
            return list(self._queue)
    
    def clear(self) -> None:
        """
        Clear all notifications from queue.
        """
        with self._lock:
            self._queue.clear()
            logger.info("Notification queue cleared")
    
    def remove(self, notification: Notification) -> bool:
        """
        Remove specific notification from queue.
        
        Args:
            notification: Notification to remove
        
        Returns:
            True if removed, False if not found
        """
        with self._lock:
            try:
                self._queue.remove(notification)
                return True
            except ValueError:
                return False
    
    def size(self) -> int:
        """
        Get current queue size.
        
        Returns:
            Number of notifications in queue
        """
        with self._lock:
            return len(self._queue)
    
    def is_empty(self) -> bool:
        """
        Check if queue is empty.
        
        Returns:
            True if queue is empty
        """
        with self._lock:
            return len(self._queue) == 0
    
    def is_full(self) -> bool:
        """
        Check if queue is at maximum size.
        
        Returns:
            True if queue is full
        """
        with self._lock:
            return len(self._queue) >= self.max_size
    
    def mark_displayed(self, notification: Notification) -> None:
        """
        Mark notification as displayed today.
        
        Used to prevent re-displaying same notification.
        
        Args:
            notification: Notification that was displayed
        """
        key = (notification.contact.name, notification.nameday_date)
        self._displayed_today.add(key)
    
    def is_displayed(self, notification: Notification) -> bool:
        """
        Check if notification was already displayed today.
        
        Args:
            notification: Notification to check
        
        Returns:
            True if already displayed
        """
        key = (notification.contact.name, notification.nameday_date)
        return key in self._displayed_today
