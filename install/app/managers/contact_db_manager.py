"""
Contact database manager providing CRUD operations [REQ-0017, REQ-0021, REQ-0029, REQ-0037, REQ-0040].

Handles all contact database operations including CSV file I/O.
"""

from pathlib import Path
from typing import List, Optional
from datetime import datetime

from app.types import Contact
from app.utils import read_csv, write_csv, ensure_directory_exists, get_logger
from app.exceptions import DatabaseException, ValidationException
from app.constants import CONTACTS_CSV_PATH, CONTACTS_CSV_HEADER, CSV_DELIMITER

logger = get_logger(__name__)


class ContactDatabaseManager:
    """
    CRUD operations for contact database [REQ-0017, REQ-0021, REQ-0029, REQ-0037, REQ-0040].
    
    Manages contact data persistence to CSV file with UTF-8 encoding and semicolon delimiter [REQ-0037].
    Provides validation of contact data before storage [REQ-0040].
    """
    
    def __init__(self, csv_path: Path = CONTACTS_CSV_PATH, validator=None):
        """
        Initialize contact database manager.
        
        Args:
            csv_path: Path to contacts CSV file
            validator: DataValidator instance for validation (optional)
        """
        self.csv_path = Path(csv_path)
        self.validator = validator
        self._contacts: List[Contact] = []
        
        # Ensure data directory exists
        ensure_directory_exists(self.csv_path.parent)
        
        # Load existing contacts
        self._load_contacts()
    
    def create_contact(self, contact: Contact) -> None:
        """
        Add new contact to database [REQ-0017, REQ-0040].
        
        Validates contact data before storage [REQ-0040] and persists to CSV [REQ-0037].
        
        Args:
            contact: Contact object to add
        
        Raises:
            ValidationException: If contact data is invalid
            DatabaseException: If save operation fails
        """
        # Validate contact
        if self.validator:
            errors = self.validator.validate_contact(contact)
            if errors:
                raise ValidationException(f"Contact validation failed: {', '.join(errors)}")
        
        try:
            contact.created_at = datetime.now()
            contact.updated_at = datetime.now()
            self._contacts.append(contact)
            self._save_contacts()
            logger.info(f"Contact created: {contact.name}")
        except Exception as e:
            raise DatabaseException(str(e), "create") from e
    
    def read_contacts(self) -> List[Contact]:
        """
        Load all contacts from CSV file [REQ-0017, REQ-0021, REQ-0037, REQ-0040].
        
        UTF-8 encoding with semicolon delimiter [REQ-0037].
        Validates loaded data [REQ-0040].
        
        Returns:
            List of all contacts
        
        Raises:
            DatabaseException: If load operation fails
        """
        try:
            return self._contacts.copy()
        except Exception as e:
            raise DatabaseException(str(e), "read") from e
    
    def update_contact(self, contact_name: str, updated: Contact) -> None:
        """
        Update existing contact [REQ-0017, REQ-0040, REQ-0037].
        
        Validates updated contact before storage [REQ-0040].
        Persists changes to CSV [REQ-0037].
        
        Args:
            contact_name: Name of contact to update
            updated: Updated contact object
        
        Raises:
            ValidationException: If contact data is invalid
            DatabaseException: If contact not found or save fails
        """
        # Validate contact
        if self.validator:
            errors = self.validator.validate_contact(updated)
            if errors:
                raise ValidationException(f"Contact validation failed: {', '.join(errors)}")
        
        try:
            for i, contact in enumerate(self._contacts):
                if contact.name == contact_name:
                    updated.created_at = contact.created_at
                    updated.updated_at = datetime.now()
                    self._contacts[i] = updated
                    self._save_contacts()
                    logger.info(f"Contact updated: {contact_name}")
                    return
            
            raise DatabaseException(f"Contact not found: {contact_name}", "update")
        except DatabaseException:
            raise
        except Exception as e:
            raise DatabaseException(str(e), "update") from e
    
    def delete_contact(self, contact_name: str) -> None:
        """
        Delete contact from database [REQ-0017, REQ-0037].
        
        Persists deletion to CSV [REQ-0037].
        
        Args:
            contact_name: Name of contact to delete
        
        Raises:
            DatabaseException: If contact not found or delete fails
        """
        try:
            for i, contact in enumerate(self._contacts):
                if contact.name == contact_name:
                    self._contacts.pop(i)
                    self._save_contacts()
                    logger.info(f"Contact deleted: {contact_name}")
                    return
            
            raise DatabaseException(f"Contact not found: {contact_name}", "delete")
        except DatabaseException:
            raise
        except Exception as e:
            raise DatabaseException(str(e), "delete") from e
    
    def get_contact_by_name(self, name: str) -> Optional[Contact]:
        """
        Find contact by name [REQ-0017].
        
        Args:
            name: Contact name to search for
        
        Returns:
            Contact object if found, None otherwise
        """
        for contact in self._contacts:
            if contact.name.lower() == name.lower():
                return contact
        return None
    
    def get_contacts_by_nameday(self, date: str) -> List[Contact]:
        """
        Find all contacts with given nameday [REQ-0017, REQ-0023].
        
        Searches both main and other namedays in MM-DD format [REQ-0023].
        
        Args:
            date: Nameday date in MM-DD format
        
        Returns:
            List of contacts with matching nameday
        """
        matches = []
        for contact in self._contacts:
            if not contact.notification_disabled:
                if contact.main_nameday == date:
                    matches.append(contact)
                elif contact.other_nameday and contact.other_nameday == date:
                    matches.append(contact)
        return matches
    
    def get_contacts_with_notifications_enabled(self) -> List[Contact]:
        """
        Get all contacts with notifications enabled [REQ-0008].
        
        Returns:
            List of contacts with notification_disabled == False
        """
        return [c for c in self._contacts if not c.notification_disabled]
    
    def disable_notifications(self, contact_name: str) -> None:
        """
        Permanently disable notifications for a contact [REQ-0008].
        
        Args:
            contact_name: Name of contact
        
        Raises:
            DatabaseException: If contact not found
        """
        contact = self.get_contact_by_name(contact_name)
        if not contact:
            raise DatabaseException(f"Contact not found: {contact_name}", "update")
        
        contact.notification_disabled = True
        self.update_contact(contact_name, contact)
    
    def enable_notifications(self, contact_name: str) -> None:
        """
        Re-enable notifications for a contact.
        
        Args:
            contact_name: Name of contact
        
        Raises:
            DatabaseException: If contact not found
        """
        contact = self.get_contact_by_name(contact_name)
        if not contact:
            raise DatabaseException(f"Contact not found: {contact_name}", "update")
        
        contact.notification_disabled = False
        self.update_contact(contact_name, contact)
    
    def get_contact_count(self) -> int:
        """
        Get total number of contacts.
        
        Returns:
            Number of contacts in database
        """
        return len(self._contacts)
    
    def _load_contacts(self) -> None:
        """
        Load contacts from CSV file [REQ-0037, REQ-0040].
        
        Private method that loads and parses CSV data.
        """
        try:
            if not self.csv_path.exists():
                logger.info(f"No existing contacts file at {self.csv_path}")
                self._contacts = []
                return
            
            rows = read_csv(self.csv_path, CSV_DELIMITER)
            self._contacts = []
            
            for row in rows:
                try:
                    contact = Contact(
                        name=row.get("name", ""),
                        main_nameday=row.get("main_nameday", ""),
                        other_nameday=row.get("other_nameday"),
                        recipient=row.get("recipient", ""),
                        email_addresses=row.get("email_addresses", ""),
                        prewritten_email=row.get("prewritten_email"),
                        comment=row.get("comment"),
                        notification_disabled=row.get("notification_disabled", "false").lower() == "true"
                    )
                    self._contacts.append(contact)
                except Exception as e:
                    logger.warning(f"Failed to parse contact row: {row}, error: {e}")
                    continue
            
            logger.info(f"Loaded {len(self._contacts)} contacts from {self.csv_path}")
        except Exception as e:
            logger.error(f"Failed to load contacts: {e}")
            self._contacts = []
    
    def _save_contacts(self) -> None:
        """
        Save contacts to CSV file [REQ-0037].
        
        Private method that writes CSV data with UTF-8 encoding and semicolon delimiter.
        """
        try:
            rows = []
            for contact in self._contacts:
                rows.append({
                    "name": contact.name,
                    "main_nameday": contact.main_nameday,
                    "other_nameday": contact.other_nameday or "",
                    "recipient": contact.recipient,
                    "email_addresses": contact.emails_as_string(),
                    "prewritten_email": contact.prewritten_email or "",
                    "comment": contact.comment or "",
                    "notification_disabled": str(contact.notification_disabled).lower()
                })
            
            write_csv(self.csv_path, rows, CONTACTS_CSV_HEADER.split(CSV_DELIMITER), CSV_DELIMITER)
            logger.info(f"Saved {len(rows)} contacts to {self.csv_path}")
        except Exception as e:
            logger.error(f"Failed to save contacts: {e}")
            raise DatabaseException(str(e), "write") from e
