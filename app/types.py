"""
Custom type definitions and data classes for the application.

Includes Contact, Notification, Settings, and other domain models.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Contact:
    """
    Data class representing a contact record [REQ-0029, REQ-0030, REQ-0031, REQ-0032, REQ-0033, REQ-0034, REQ-0035, REQ-0036].
    
    Attributes:
        name: Contact's name (required) [REQ-0030]
        main_nameday: Main nameday date in MM-DD format (required) [REQ-0031, REQ-0023]
        other_nameday: Optional secondary nameday in MM-DD format [REQ-0032, REQ-0023]
        recipient: Recipient label/description (required) [REQ-0033]
        email_addresses: List of email addresses for the contact [REQ-0034]
        prewritten_email: Optional email template [REQ-0035]
        comment: Optional free-text comment [REQ-0036]
        notification_disabled: Whether notifications are disabled (Done button state) [REQ-0008]
        created_at: Timestamp when contact was created
        updated_at: Timestamp when contact was last updated
    """
    
    name: str
    main_nameday: str
    recipient: str
    email_addresses: List[str] = field(default_factory=list)
    other_nameday: Optional[str] = None
    prewritten_email: Optional[str] = None
    comment: Optional[str] = None
    notification_disabled: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Validate contact data after initialization."""
        if isinstance(self.email_addresses, str):
            # Support comma/semicolon-separated string input
            self.email_addresses = [e.strip() for e in self.email_addresses.replace(",", ";").split(";") if e.strip()]
    
    def get_email_list(self) -> List[str]:
        """Return list of valid email addresses."""
        return self.email_addresses if isinstance(self.email_addresses, list) else []
    
    def emails_as_string(self) -> str:
        """Return email addresses as semicolon-separated string."""
        return ";".join(self.email_addresses) if isinstance(self.email_addresses, list) else ""


@dataclass
class Notification:
    """
    Data class representing a notification to be displayed [REQ-0005, REQ-0006, REQ-0007, REQ-0008, REQ-0044].
    
    Attributes:
        contact: Contact object associated with this notification
        nameday_date: Nameday date in MM-DD format [REQ-0023]
        timestamp: When the notification was created
        is_deferred: Whether this notification has been deferred
        deferred_until: When to show the deferred notification
        displayed: Whether the notification has been shown to user
        action_taken: What action user took (None, 'later', 'mail', 'done')
    """
    
    contact: Contact
    nameday_date: str
    timestamp: datetime = field(default_factory=datetime.now)
    is_deferred: bool = False
    deferred_until: Optional[datetime] = None
    displayed: bool = False
    action_taken: Optional[str] = None  # 'later', 'mail', 'done', None
    
    def __hash__(self):
        """Make notification hashable for queue operations."""
        return hash((self.contact.name, self.nameday_date, self.timestamp))


@dataclass
class Nameday:
    """
    Data class for nameday reference data [REQ-0018, REQ-0038, REQ-0039, REQ-0023].
    
    Attributes:
        name: Person's name
        main_nameday: Main nameday date in MM-DD format [REQ-0023]
        other_nameday: Optional secondary nameday in MM-DD format [REQ-0023]
    """
    
    name: str
    main_nameday: str
    other_nameday: Optional[str] = None


@dataclass
class Settings:
    """
    Data class for application settings [REQ-0014, REQ-0026, REQ-0028, REQ-0055].
    
    Attributes:
        check_interval: Minutes between nameday checks [REQ-0003]
        auto_launch: Enable auto-launch at startup [REQ-0002]
        language: Application language [REQ-0045]
        gmail_account: Gmail account email for SMTP [REQ-0016]
        gmail_password: Gmail account password or app token [REQ-0016]
        notifications_enabled: Whether notifications are globally enabled [REQ-0014]
    """
    
    check_interval: int = 15  # Default 15 min [REQ-0003]
    auto_launch: bool = False  # [REQ-0002]
    language: str = "en"  # [REQ-0045]
    gmail_account: str = ""  # [REQ-0016]
    gmail_password: str = ""  # [REQ-0016]
    notifications_enabled: bool = True  # [REQ-0014]
    
    def to_dict(self) -> dict:
        """Convert settings to dictionary for JSON serialization."""
        return {
            "check_interval": self.check_interval,
            "auto_launch": self.auto_launch,
            "language": self.language,
            "gmail_account": self.gmail_account,
            "gmail_password": self.gmail_password,
            "notifications_enabled": self.notifications_enabled,
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Settings":
        """Create Settings from dictionary (e.g., from JSON)."""
        return cls(
            check_interval=data.get("check_interval", 15),
            auto_launch=data.get("auto_launch", False),
            language=data.get("language", "en"),
            gmail_account=data.get("gmail_account", ""),
            gmail_password=data.get("gmail_password", ""),
            notifications_enabled=data.get("notifications_enabled", True),
        )


@dataclass
class ValidationError:
    """
    Data class for validation error information.
    
    Attributes:
        field: Name of field that failed validation
        message: Error message
        value: The invalid value
    """
    
    field: str
    message: str
    value: Optional[str] = None
    
    def __str__(self) -> str:
        """Return formatted error message."""
        if self.value:
            return f"{self.field}: {self.message} (got '{self.value}')"
        return f"{self.field}: {self.message}"
