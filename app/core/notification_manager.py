"""
Notification manager for handling notifications [REQ-0005, REQ-0006, REQ-0007, REQ-0008, REQ-0009].

Manages notification display, user interactions, and queue processing.
"""

from typing import Optional, Callable
from datetime import datetime, timedelta

from app.types import Notification, Contact
from app.utils import get_logger
from app.exceptions import NotificationException

logger = get_logger(__name__)


class NotificationManager:
    """
    Manages notification display, queue, and user interactions [REQ-0005, REQ-0006, REQ-0007, REQ-0008, REQ-0044].
    
    Handles the three action buttons: Later [REQ-0006], Mail [REQ-0007], Done [REQ-0008].
    Displays modal dialogs [REQ-0005, REQ-0043, REQ-0044].
    Manages notification queue and state.
    """
    
    def __init__(
        self,
        email_service=None,  # EmailService
        contact_db=None,  # ContactDatabaseManager
        notification_queue=None  # NotificationQueue
    ):
        """
        Initialize notification manager.
        
        Args:
            email_service: EmailService instance for sending emails [REQ-0007]
            contact_db: ContactDatabaseManager for contact operations
            notification_queue: NotificationQueue instance
        """
        self.email_service = email_service
        self.contact_db = contact_db
        self.notification_queue = notification_queue
        
        self._current_notification: Optional[Notification] = None
        self._notification_callbacks = {
            "completed": [],
            "deferred": [],
            "mail_sent": [],
            "disabled": []
        }
    
    def queue_notification(self, notification: Notification) -> None:
        """
        Add notification to display queue [REQ-0004, REQ-0009].
        
        Supports multiple namedays on same day [REQ-0004].
        
        Args:
            notification: Notification to queue
        """
        if self.notification_queue:
            self.notification_queue.add(notification)
            logger.info(f"Notification queued: {notification.contact.name}")
    
    def show_notification(self, notification: Notification) -> None:
        """
        Display notification modal [REQ-0005, REQ-0043, REQ-0044].
        
        Modal is focused and blocking [REQ-0005].
        Should be called from UI thread.
        Displays contact info and action buttons.
        
        Args:
            notification: Notification to display
        
        Note:
            This is called from UI code that provides the actual PyQt5 modal.
            This method handles the notification state and callbacks.
        """
        self._current_notification = notification
        notification.displayed = True
        
        logger.info(f"Notification displayed: {notification.contact.name}")
    
    def handle_later_button(self, notification: Notification, defer_minutes: int = 15) -> None:
        """
        Reschedule notification for next interval [REQ-0006].
        
        Closes modal and returns to background.
        Notification will be re-queued at next monitoring cycle.
        
        Args:
            notification: Notification to defer
            defer_minutes: Minutes until next check
        """
        try:
            notification.is_deferred = True
            notification.deferred_until = datetime.now() + timedelta(minutes=defer_minutes)
            
            # Re-queue the notification
            if self.notification_queue:
                self.notification_queue.add(notification)
            
            logger.info(f"Notification deferred: {notification.contact.name} for {defer_minutes} min")
            
            # Fire callback
            for callback in self._notification_callbacks["deferred"]:
                callback(notification)
        
        except Exception as e:
            logger.error(f"Error deferring notification: {e}")
            raise NotificationException(f"Failed to defer notification: {e}") from e
    
    def handle_mail_button(self, contact: Contact) -> bool:
        """
        Send email to contact [REQ-0007, REQ-0019, REQ-0020].
        
        Only triggered by explicit user action [REQ-0019].
        Disable notifications on success [REQ-0008].
        Uses prewritten template if available [REQ-0020].
        
        Args:
            contact: Contact to email
        
        Returns:
            True if sent successfully, False otherwise
        """
        try:
            if not self.email_service:
                logger.warning("Email service not configured")
                return False
            
            email_addresses = contact.get_email_list()
            if not email_addresses:
                logger.warning(f"No email addresses for {contact.name}")
                return False
            
            # Send email [REQ-0007, REQ-0052]
            success = self.email_service.send_to_contact(
                email_addresses,
                contact.name,
                contact.prewritten_email  # [REQ-0020]
            )
            
            if success:
                logger.info(f"Email sent to {contact.name}")
                
                # Disable notifications [REQ-0008]
                self.handle_done_button(contact, silent=True)
                
                # Fire callback
                for callback in self._notification_callbacks["mail_sent"]:
                    callback(contact)
            
            return success
        
        except Exception as e:
            logger.error(f"Error sending email to {contact.name}: {e}")
            return False
    
    def handle_done_button(self, contact: Contact, silent: bool = False) -> None:
        """
        Permanently disable notifications [REQ-0008].
        
        Shows user warning about irreversibility (unless silent=True).
        Updates database to mark notifications as disabled.
        
        Args:
            contact: Contact to disable notifications for
            silent: If True, don't show warning (used internally)
        
        Raises:
            NotificationException: If database update fails
        """
        try:
            if not silent:
                # In UI context, would show warning dialog
                logger.info(f"Disabling notifications for {contact.name}")
            
            # Update contact in database [REQ-0008]
            if self.contact_db:
                self.contact_db.disable_notifications(contact.name)
            
            logger.info(f"Notifications disabled for {contact.name}")
            
            # Fire callback
            for callback in self._notification_callbacks["disabled"]:
                callback(contact)
        
        except Exception as e:
            logger.error(f"Error disabling notifications: {e}")
            raise NotificationException(f"Failed to disable notifications: {e}") from e
    
    def process_queue(self) -> Optional[Notification]:
        """
        Process notification queue, return next to display.
        
        Retrieves next queued notification without removing it.
        UI code should call this repeatedly to show all notifications.
        
        Returns:
            Next Notification to display, or None if queue empty
        """
        if not self.notification_queue:
            return None
        
        return self.notification_queue.peek_next()
    
    def get_queue_count(self) -> int:
        """
        Get number of pending notifications [REQ-0009].
        
        Returns:
            Count of notifications in queue
        """
        if self.notification_queue:
            return self.notification_queue.size()
        return 0
    
    def register_callback(self, event: str, callback: Callable) -> None:
        """
        Register callback for notification events.
        
        Args:
            event: Event name ("completed", "deferred", "mail_sent", "disabled")
            callback: Callable to invoke on event
        """
        if event in self._notification_callbacks:
            self._notification_callbacks[event].append(callback)
    
    def clear_queue(self) -> None:
        """
        Clear all pending notifications [REQ-0009].
        """
        if self.notification_queue:
            self.notification_queue.clear()
            logger.info("Notification queue cleared")
    
    def get_current_notification(self) -> Optional[Notification]:
        """
        Get currently displayed notification.
        
        Returns:
            Current notification or None
        """
        return self._current_notification
    
    def notification_handled(self, notification: Notification) -> None:
        """
        Mark notification as handled and remove from queue.
        
        Args:
            notification: Notification that was handled
        """
        if self.notification_queue:
            self.notification_queue.remove(notification)
            
            # Fire completed callback
            for callback in self._notification_callbacks["completed"]:
                callback(notification)
