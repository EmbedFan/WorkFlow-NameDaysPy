"""
Data validator for input validation [REQ-0040].

Validates all input data before storage to ensure data integrity.
"""

import re
from typing import List, Optional

from app.types import Contact, ValidationError
from app.utils.date_utils import is_valid_nameday_date
from app.constants import EMAIL_PATTERN, NAMEDAY_DATE_FORMAT

logger_module = None  # Lazy import to avoid circular dependency


def get_logger():
    """Get logger lazily."""
    global logger_module
    if logger_module is None:
        from app.utils import get_logger
        logger_module = get_logger(__name__)
    return logger_module


class DataValidator:
    """
    Validate all input data before storage [REQ-0040].
    
    Provides validation for Contact records, email addresses, dates, and other data types.
    """
    
    def validate_contact(self, contact: Contact) -> List[str]:
        """
        Validate contact record [REQ-0040].
        
        Checks all contact fields for validity.
        
        Args:
            contact: Contact object to validate
        
        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []
        
        # Validate name (required, non-empty) [REQ-0030]
        if not self.validate_name(contact.name):
            errors.append("Name is required and cannot be empty")
        
        # Validate main nameday (required, MM-DD format) [REQ-0031, REQ-0023]
        if not self.validate_nameday_date(contact.main_nameday):
            errors.append(f"Main nameday must be in MM-DD format, got '{contact.main_nameday}'")
        
        # Validate other nameday if provided (MM-DD format) [REQ-0032, REQ-0023]
        if contact.other_nameday and not self.validate_nameday_date(contact.other_nameday):
            errors.append(f"Other nameday must be in MM-DD format, got '{contact.other_nameday}'")
        
        # Validate recipient (required, non-empty) [REQ-0033]
        if not self.validate_recipient(contact.recipient):
            errors.append("Recipient label is required and cannot be empty")
        
        # Validate email addresses [REQ-0034, REQ-0040]
        if contact.email_addresses:
            email_list = contact.get_email_list() if hasattr(contact, 'get_email_list') else contact.email_addresses
            if email_list:
                for email in email_list:
                    if email and not self.validate_email(email):
                        errors.append(f"Invalid email address: '{email}'")
        
        return errors
    
    def validate_nameday_date(self, date: str) -> bool:
        """
        Validate MM-DD format [REQ-0023, REQ-0040].
        
        Args:
            date: Date string to validate
        
        Returns:
            True if valid MM-DD format, False otherwise
        """
        if not date or not isinstance(date, str):
            return False
        
        return is_valid_nameday_date(date)
    
    def validate_email(self, email: str) -> bool:
        """
        Validate email address format [REQ-0034, REQ-0040].
        
        Args:
            email: Email address to validate
        
        Returns:
            True if valid email format, False otherwise
        """
        if not email or not isinstance(email, str):
            return False
        
        email = email.strip()
        if not email or len(email) > 254:
            return False
        
        return bool(re.match(EMAIL_PATTERN, email))
    
    def validate_name(self, name: str) -> bool:
        """
        Validate name (non-empty text) [REQ-0030, REQ-0040].
        
        Args:
            name: Name to validate
        
        Returns:
            True if valid, False otherwise
        """
        if not name or not isinstance(name, str):
            return False
        
        return len(name.strip()) > 0
    
    def validate_recipient(self, recipient: str) -> bool:
        """
        Validate recipient label (non-empty) [REQ-0033, REQ-0040].
        
        Args:
            recipient: Recipient label to validate
        
        Returns:
            True if valid, False otherwise
        """
        if not recipient or not isinstance(recipient, str):
            return False
        
        return len(recipient.strip()) > 0
    
    def validate_check_interval(self, minutes: int) -> bool:
        """
        Validate check interval in minutes.
        
        Args:
            minutes: Interval in minutes
        
        Returns:
            True if valid interval, False otherwise
        """
        from app.constants import MIN_CHECK_INTERVAL, MAX_CHECK_INTERVAL
        
        if not isinstance(minutes, int):
            return False
        
        return MIN_CHECK_INTERVAL <= minutes <= MAX_CHECK_INTERVAL
    
    def validate_language(self, language: str) -> bool:
        """
        Validate language code [REQ-0045].
        
        Args:
            language: Language code to validate
        
        Returns:
            True if valid language, False otherwise
        """
        from app.constants import SUPPORTED_LANGUAGES
        
        if not language or not isinstance(language, str):
            return False
        
        return language in SUPPORTED_LANGUAGES
    
    def sanitize_name(self, name: str) -> str:
        """
        Sanitize and normalize a name string.
        
        Args:
            name: Name to sanitize
        
        Returns:
            Sanitized name
        """
        if not name:
            return ""
        
        # Strip whitespace and limit length
        sanitized = name.strip()[:255]
        
        return sanitized
    
    def sanitize_email(self, email: str) -> str:
        """
        Sanitize and normalize an email address.
        
        Args:
            email: Email to sanitize
        
        Returns:
            Sanitized email (lowercase, trimmed)
        """
        if not email:
            return ""
        
        sanitized = email.strip().lower()[:254]
        
        return sanitized
    
    def parse_email_list(self, email_string: str) -> List[str]:
        """
        Parse comma or semicolon-separated email addresses.
        
        Args:
            email_string: Email addresses separated by comma or semicolon
        
        Returns:
            List of email addresses (validated)
        """
        if not email_string or not isinstance(email_string, str):
            return []
        
        # Split by comma or semicolon
        emails = re.split(r'[,;]', email_string)
        
        # Clean and validate
        valid_emails = []
        for email in emails:
            email = email.strip()
            if email and self.validate_email(email):
                valid_emails.append(email)
        
        return valid_emails
