# Name Days Monitoring App - Implementation Plan

## 1. Technology Stack

### Core Dependencies
```
Python: 3.7+
PyQt5: 5.15+              [REQ-0041] UI Framework
python-dotenv: 0.19+      Configuration management
pysmtplib: Built-in       Email via SMTP [REQ-0052]
winreg: Windows-specific  Registry operations [REQ-0051]
psutil: 5.8+              Memory monitoring [REQ-0024]
```

### Development Tools
```
pytest: 7.0+              Unit testing
pytest-cov: 3.0+          Coverage reporting
black: 22.0+              Code formatting
pylint: 2.10+             Code linting
```

### External Services
```
Gmail SMTP: smtp.gmail.com [REQ-0016, REQ-0052]
Windows Registry: HKEY_CURRENT_USER [REQ-0051]
```

---

## 2. Module Breakdown & File Structure

```
NameDaysMonitoringApp/
├── app/
│   ├── __init__.py
│   ├── main.py                          Application entry point [REQ-0001]
│   ├── constants.py                     App-wide constants
│   ├── types.py                         Custom type definitions
│   ├── exceptions.py                    Custom exceptions
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── monitoring_engine.py         Background monitoring [REQ-0022]
│   │   ├── notification_manager.py      Notification handling [REQ-0005-0008]
│   │   └── notification_queue.py        Notification queuing
│   │
│   ├── managers/
│   │   ├── __init__.py
│   │   ├── contact_db_manager.py        CRUD operations [REQ-0017]
│   │   ├── nameday_reference_manager.py Nameday lookup [REQ-0018]
│   │   ├── settings_manager.py          Settings persistence [REQ-0026]
│   │   └── config_validator.py          Configuration validation
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── email_service.py             Gmail integration [REQ-0016, REQ-0052]
│   │   ├── windows_startup.py           Auto-launch setup [REQ-0002, REQ-0051]
│   │   └── data_validator.py            Input validation [REQ-0040]
│   │
│   ├── ui/
│   │   ├── __init__.py
│   │   ├── system_tray.py               System tray icon [REQ-0010, REQ-0042]
│   │   ├── notification_modal.py        Modal dialog [REQ-0005, REQ-0043, REQ-0044]
│   │   ├── settings_dialog.py           Settings UI [REQ-0014, REQ-0047]
│   │   ├── database_editor.py           Contact management [REQ-0011, REQ-0049]
│   │   ├── query_dialog.py              Nameday search [REQ-0013, REQ-0050]
│   │   ├── today_namedays_view.py       Show today's names [REQ-0012]
│   │   ├── styles.py                    QSS stylesheet management
│   │   └── utils_ui.py                  UI utility functions
│   │
│   ├── i18n/
│   │   ├── __init__.py
│   │   ├── i18n_manager.py              Language support [REQ-0045, REQ-0046]
│   │   ├── en.json                      English strings
│   │   └── hu.json                      Hungarian strings
│   │
│   └── utils/
│       ├── __init__.py
│       ├── logger.py                    Logging utility
│       ├── file_utils.py                File operations
│       ├── date_utils.py                MM-DD format handling [REQ-0023]
│       └── error_handler.py             Error handling [REQ-0027]
│
├── resources/
│   ├── namedays.csv                     Built-in nameday data [REQ-0018, REQ-0039]
│   ├── app_icon.png                     System tray icon
│   └── styles/
│       └── default.qss                  Qt stylesheets
│
├── tests/
│   ├── __init__.py
│   ├── test_contact_db_manager.py
│   ├── test_nameday_reference_manager.py
│   ├── test_settings_manager.py
│   ├── test_email_service.py
│   ├── test_monitoring_engine.py
│   ├── test_data_validator.py
│   └── test_ui_components.py
│
├── docs/
│   ├── system_design.md                 System design document
│   ├── architecture_diagram.svg         Architecture visualization
│   ├── implementation.md                This file
│   ├── API.md                           API documentation
│   └── SETUP.md                         Installation guide
│
├── requirements.txt                     Python dependencies
├── setup.py                             Package setup
├── main.py                              Entry point script
└── README.md                            Project readme
```

---

## 3. Class and Function Definitions

### 3.1 Core Classes

#### `app/main.py` - Application Entry Point
```python
class NameDaysMonitoringApp(QApplication):
    """
    Main application class. Initializes the application and manages
    lifecycle.
    
    Requirements: REQ-0001, REQ-0002, REQ-0015, REQ-0041
    """
    
    def __init__(self):
        """Initialize application."""
        super().__init__()
        
    def setup_ui(self) -> None:
        """Create UI components (tray icon, hidden main window)."""
        
    def setup_managers(self) -> None:
        """Initialize all manager instances."""
        
    def start_monitoring(self) -> None:
        """Start background monitoring thread [REQ-0022]."""
        
    def detect_auto_launch(self) -> bool:
        """Detect if app started at Windows startup [REQ-0002]."""
        
    def cleanup(self) -> None:
        """Graceful shutdown [REQ-0015]."""
    
    def run(self) -> int:
        """Run application event loop."""
```

#### `app/core/monitoring_engine.py` - Background Monitoring
```python
class MonitoringEngine(QThread):
    """
    Background monitoring thread that checks for namedays at
    configured intervals.
    
    Requirements: REQ-0003, REQ-0022, REQ-0024
    """
    
    # Signals
    nameday_found = pyqtSignal(list)  # List[Notification]
    interval_changed = pyqtSignal(int)
    
    def __init__(self, contact_db: ContactDatabaseManager,
                 nameday_ref: NamedayReferenceManager,
                 settings: SettingsManager):
        """Initialize monitoring engine."""
        super().__init__()
        
    def start_monitoring(self) -> None:
        """Start background monitoring loop [REQ-0022]."""
        
    def stop_monitoring(self) -> None:
        """Stop monitoring gracefully."""
        
    def run(self) -> None:
        """QThread run method - main monitoring loop."""
        
    def check_namedays(self) -> List['Notification']:
        """
        Query databases and find today's namedays.
        Returns list of Notification objects [REQ-0004].
        """
        
    def set_interval(self, minutes: int) -> None:
        """
        Update check interval. Changes apply without restart [REQ-0003].
        """
        
    def _get_today_date(self) -> str:
        """Get today's date in MM-DD format [REQ-0023]."""
        
    def _match_contacts(self, nameday_names: List[str]) -> List['Contact']:
        """
        Find all contacts with matching namedays.
        Supports multiple same-day namedays [REQ-0004].
        """


class Notification:
    """Data class representing a notification."""
    
    contact: 'Contact'
    nameday_date: str  # MM-DD format [REQ-0023]
    timestamp: datetime
    is_deferred: bool
    deferred_until: Optional[datetime]
```

#### `app/core/notification_manager.py` - Notification Handling
```python
class NotificationManager(QObject):
    """
    Manages notification display, queue, and user interactions
    (Later, Mail, Done buttons).
    
    Requirements: REQ-0005, REQ-0006, REQ-0007, REQ-0008,
                  REQ-0009, REQ-0043, REQ-0044
    """
    
    # Signals
    notification_completed = pyqtSignal(Notification)
    notification_deferred = pyqtSignal(Notification)
    
    def __init__(self, email_service: 'EmailService',
                 contact_db: 'ContactDatabaseManager'):
        """Initialize notification manager."""
        super().__init__()
        
    def queue_notification(self, notification: Notification) -> None:
        """
        Add notification to display queue [REQ-0004].
        Support multiple namedays same day.
        """
        
    def show_notification(self, notification: Notification) -> None:
        """
        Display notification modal [REQ-0005, REQ-0043, REQ-0044].
        Modal is focused and blocking [REQ-0005].
        """
        
    def handle_later_button(self, notification: Notification) -> None:
        """
        Reschedule notification for next interval [REQ-0006].
        Close modal and return to background.
        """
        
    def handle_mail_button(self, contact: 'Contact') -> bool:
        """
        Send email to contact [REQ-0007].
        Only triggered by explicit user action [REQ-0019].
        Disable notifications on success.
        Returns: True if sent successfully.
        """
        
    def handle_done_button(self, contact: 'Contact') -> None:
        """
        Permanently disable notifications [REQ-0008].
        Show user warning about irreversibility.
        Update database.
        """
        
    def process_queue(self) -> None:
        """Process notification queue, display one at a time."""
        
    def get_queue_count(self) -> int:
        """Get number of pending notifications."""
```

#### `app/managers/contact_db_manager.py` - Contact Database
```python
class Contact:
    """
    Data class representing a contact record.
    
    Requirements: REQ-0029, REQ-0030, REQ-0031, REQ-0032, REQ-0033,
                  REQ-0034, REQ-0035, REQ-0036
    """
    
    name: str                               # Required [REQ-0030]
    main_nameday: str                       # MM-DD format [REQ-0031, REQ-0023]
    other_nameday: Optional[str]            # Optional MM-DD [REQ-0032, REQ-0023]
    recipient: str                          # Required label [REQ-0033]
    email_addresses: List[str]              # Comma-separated [REQ-0034]
    prewritten_email: Optional[str]         # Template [REQ-0035]
    comment: Optional[str]                  # Free text [REQ-0036]
    notification_disabled: bool             # Done button state [REQ-0008]


class ContactDatabaseManager:
    """
    CRUD operations for contact database.
    
    Requirements: REQ-0017, REQ-0021, REQ-0029, REQ-0037, REQ-0040
    """
    
    def __init__(self, csv_path: str, validator: 'DataValidator'):
        """Initialize contact database manager."""
        
    def create_contact(self, contact: Contact) -> None:
        """
        Add new contact [REQ-0017].
        Validate before storage [REQ-0040].
        Persist to CSV [REQ-0037].
        """
        
    def read_contacts(self) -> List[Contact]:
        """
        Load all contacts from CSV [REQ-0017, REQ-0021].
        UTF-8 encoding, semicolon delimiter [REQ-0037].
        Validate data [REQ-0040].
        """
        
    def update_contact(self, contact_id: str, 
                      updated: Contact) -> None:
        """
        Update existing contact [REQ-0017].
        Validate before storage [REQ-0040].
        Persist to CSV [REQ-0037].
        """
        
    def delete_contact(self, contact_id: str) -> None:
        """
        Delete contact from database [REQ-0017].
        Persist to CSV [REQ-0037].
        """
        
    def get_contact_by_name(self, name: str) -> Optional[Contact]:
        """Find contact by name [REQ-0017]."""
        
    def get_contacts_by_nameday(self, date: str) -> List[Contact]:
        """
        Find all contacts with given nameday [REQ-0017, REQ-0023].
        Date format: MM-DD.
        """
        
    def validate_contact(self, contact: Contact) -> List[str]:
        """
        Validate contact data [REQ-0040].
        Returns: List of validation error messages.
        """
        
    def _load_csv(self) -> List[Contact]:
        """Load contacts from CSV file [REQ-0037]."""
        
    def _save_csv(self, contacts: List[Contact]) -> None:
        """Save contacts to CSV file [REQ-0037]."""
```

#### `app/managers/nameday_reference_manager.py` - Nameday Lookup
```python
class Nameday:
    """Data class for nameday reference."""
    
    name: str
    main_nameday: str  # MM-DD format [REQ-0023]
    other_nameday: Optional[str]  # MM-DD or empty [REQ-0023]


class NamedayReferenceManager:
    """
    Query and manage built-in nameday reference database.
    
    Requirements: REQ-0013, REQ-0018, REQ-0038, REQ-0039, REQ-0023
    """
    
    def __init__(self, csv_path: str):
        """Initialize with reference CSV [REQ-0039]."""
        
    def get_nameday(self, name: str) -> Optional[Nameday]:
        """
        Lookup nameday by name [REQ-0018].
        Case handling per language [REQ-0013].
        """
        
    def get_names_for_date(self, date: str) -> List[str]:
        """
        Find all names with given nameday date [REQ-0018].
        Date format: MM-DD [REQ-0023].
        """
        
    def get_all_names(self) -> List[str]:
        """Get all available names [REQ-0018]."""
        
    def search_names(self, pattern: str) -> List[str]:
        """
        Search names by pattern [REQ-0013].
        Case handling per language and implementation.
        """
        
    def _load_reference(self) -> List[Nameday]:
        """Load reference from CSV [REQ-0039]."""
        
    def _validate_date_format(self, date: str) -> bool:
        """Validate MM-DD format [REQ-0023]."""
```

#### `app/managers/settings_manager.py` - Configuration Management
```python
class Settings:
    """Data class for application settings."""
    
    check_interval: int = 15               # Default 15 min [REQ-0003]
    auto_launch: bool = False              # [REQ-0002]
    language: str = "en"                   # [REQ-0045]
    gmail_account: str = ""                # [REQ-0016]
    gmail_password: str = ""               # [REQ-0016]
    notifications_enabled: bool = True     # [REQ-0014]


class SettingsManager(QObject):
    """
    Manage application settings with persistence.
    
    Requirements: REQ-0014, REQ-0026, REQ-0028, REQ-0055
    """
    
    # Signals
    settings_changed = pyqtSignal(str)  # Setting key changed
    
    def __init__(self, config_path: str):
        """Initialize settings manager [REQ-0026]."""
        
    def load_settings(self) -> Settings:
        """
        Load settings from config file [REQ-0026].
        Apply defaults if missing [REQ-0028].
        """
        
    def save_settings(self, settings: Settings) -> None:
        """Save settings to config file [REQ-0026]."""
        
    def get_setting(self, key: str) -> Any:
        """Get individual setting value [REQ-0026]."""
        
    def set_setting(self, key: str, value: Any) -> None:
        """Update individual setting and save [REQ-0026]."""
        
    def reset_to_defaults(self) -> None:
        """
        Reset all settings to defaults [REQ-0028].
        Useful for corrupted config recovery.
        """
        
    def is_valid(self) -> bool:
        """Check if current settings are valid."""
        
    def _create_default_config(self) -> None:
        """Create default config file [REQ-0028]."""
```

#### `app/services/email_service.py` - Gmail Integration
```python
class EmailService:
    """
    Send emails via Gmail SMTP/OAuth2.
    
    Requirements: REQ-0007, REQ-0016, REQ-0019, REQ-0020, REQ-0052
    """
    
    def __init__(self, settings: 'SettingsManager'):
        """Initialize email service with settings [REQ-0016]."""
        
    def send_email(self, to_addresses: List[str],
                  subject: str,
                  body: str,
                  template: Optional[str] = None) -> bool:
        """
        Send email to recipients [REQ-0007].
        Only called on explicit Mail button click [REQ-0019].
        Apply prewritten template if provided [REQ-0020].
        
        Returns: True if sent successfully, False otherwise.
        Handle failures gracefully [REQ-0027].
        """
        
    def authenticate(self, email: str, password: str) -> bool:
        """
        Authenticate with Gmail account [REQ-0016, REQ-0052].
        
        Returns: True if authenticated successfully.
        """
        
    def validate_email_address(self, email: str) -> bool:
        """
        Validate email address format [REQ-0040].
        
        Returns: True if valid format.
        """
        
    def _apply_template(self, template: str, 
                       contact: 'Contact') -> str:
        """Apply prewritten email template [REQ-0020]."""
        
    def _send_smtp(self, to_addresses: List[str],
                   subject: str,
                   body: str) -> bool:
        """Send email via SMTP [REQ-0052]."""
```

#### `app/services/windows_startup.py` - Auto-Launch Management
```python
class WindowsStartupManager:
    """
    Manage Windows startup integration.
    
    Requirements: REQ-0002, REQ-0051
    """
    
    def __init__(self):
        """Initialize Windows startup manager [REQ-0051]."""
        
    def enable_auto_launch(self, app_path: str) -> bool:
        """
        Register application for auto-launch at startup [REQ-0002, REQ-0051].
        Configure Windows registry entry.
        
        Returns: True if successful.
        """
        
    def disable_auto_launch(self) -> bool:
        """
        Unregister application from auto-launch [REQ-0002, REQ-0051].
        Remove Windows registry entry.
        
        Returns: True if successful.
        """
        
    def is_auto_launch_enabled(self) -> bool:
        """
        Check if auto-launch is currently enabled [REQ-0002].
        
        Returns: True if enabled.
        """
        
    def is_running_at_startup(self) -> bool:
        """
        Detect if application started at system startup [REQ-0002].
        
        Returns: True if started by Windows at boot.
        """
        
    def _get_registry_path(self) -> str:
        """Get registry key path for app startup."""
        
    def _write_registry(self, value: str) -> bool:
        """Write to Windows registry."""
        
    def _read_registry(self) -> Optional[str]:
        """Read from Windows registry."""
        
    def _delete_registry(self) -> bool:
        """Delete registry key."""
```

#### `app/services/data_validator.py` - Input Validation
```python
class DataValidator:
    """
    Validate all input data before storage.
    
    Requirements: REQ-0040
    """
    
    def validate_contact(self, contact: 'Contact') -> List[str]:
        """
        Validate contact record [REQ-0040].
        
        Returns: List of validation error messages (empty if valid).
        """
        
    def validate_nameday_date(self, date: str) -> bool:
        """
        Validate MM-DD format [REQ-0023, REQ-0040].
        
        Returns: True if valid.
        """
        
    def validate_email(self, email: str) -> bool:
        """
        Validate email address format [REQ-0034, REQ-0040].
        
        Returns: True if valid.
        """
        
    def validate_name(self, name: str) -> bool:
        """
        Validate name (non-empty text) [REQ-0030, REQ-0040].
        
        Returns: True if valid.
        """
        
    def validate_recipient(self, recipient: str) -> bool:
        """
        Validate recipient label (non-empty) [REQ-0033, REQ-0040].
        
        Returns: True if valid.
        """
        
    def _parse_email_list(self, email_str: str) -> List[str]:
        """Parse comma-separated email list [REQ-0034]."""
        
    def _is_valid_date_format(self, date: str) -> bool:
        """Check MM-DD format strictly."""
```

### 3.2 UI Classes

#### `app/ui/system_tray.py` - System Tray Icon
```python
class SystemTrayManager(QObject):
    """
    Manage system tray icon and context menu.
    
    Requirements: REQ-0010, REQ-0042
    """
    
    # Signals
    menu_show_all_names = pyqtSignal()      # REQ-0012
    menu_query_nameday = pyqtSignal()       # REQ-0013
    menu_settings = pyqtSignal()            # REQ-0014
    menu_edit_database = pyqtSignal()       # REQ-0011
    menu_exit = pyqtSignal()                # REQ-0015
    
    def __init__(self, app: QApplication):
        """Initialize tray manager [REQ-0010, REQ-0042]."""
        super().__init__()
        
    def setup_tray_icon(self) -> None:
        """
        Create and configure system tray icon [REQ-0010, REQ-0042].
        Icon visible in system tray.
        """
        
    def setup_context_menu(self) -> None:
        """
        Create context menu [REQ-0010].
        Menu items: Show All, Query, Settings, Edit DB, Exit.
        """
        
    def show_message(self, title: str, message: str) -> None:
        """Show tray notification message."""
        
    def set_icon_state(self, active: bool) -> None:
        """Update icon appearance (active/inactive)."""
```

#### `app/ui/notification_modal.py` - Notification Dialog
```python
class NotificationModal(QDialog):
    """
    Modal dialog displaying nameday notification.
    
    Requirements: REQ-0005, REQ-0009, REQ-0043, REQ-0044
    """
    
    # Signals
    later_clicked = pyqtSignal()
    mail_clicked = pyqtSignal()
    done_clicked = pyqtSignal()
    
    def __init__(self, contact: 'Contact', 
                 important_connections: List[str],
                 parent=None):
        """
        Initialize notification modal [REQ-0005, REQ-0043, REQ-0044].
        
        Modal:
        - Displays contact nameday info [REQ-0009]
        - Shows "Important connections" list [REQ-0009]
        - Three buttons: [Later] [Mail] [Done] [REQ-0044]
        - Focused and blocking [REQ-0005]
        """
        super().__init__(parent)
        
    def setup_ui(self) -> None:
        """
        Create modal layout [REQ-0043, REQ-0044].
        
        Display format:
        "Today name days: [name]"
        "Important connections with this name:"
        [connection list]
        [Later] [Mail] [Done]
        """
        
    def setup_buttons(self) -> None:
        """Create three action buttons horizontally [REQ-0044]."""
        
    def enable_mail_button(self, enabled: bool) -> None:
        """Enable/disable Mail button based on email availability."""
        
    def show_warning(self, title: str, message: str) -> None:
        """Show warning dialog (e.g., Done button confirmation)."""
        
    def closeEvent(self, event: QCloseEvent) -> None:
        """Handle modal close event."""
```

#### `app/ui/settings_dialog.py` - Settings UI
```python
class SettingsDialog(QDialog):
    """
    Settings configuration dialog.
    
    Requirements: REQ-0014, REQ-0047, REQ-0002, REQ-0003, REQ-0045, REQ-0016
    """
    
    # Signals
    settings_applied = pyqtSignal(dict)
    
    def __init__(self, settings_manager: 'SettingsManager',
                 startup_manager: 'WindowsStartupManager',
                 parent=None):
        """Initialize settings dialog [REQ-0047]."""
        super().__init__(parent)
        
    def setup_ui(self) -> None:
        """
        Create settings form [REQ-0047].
        
        Fields:
        - Check interval input [REQ-0003]
        - Auto-launch checkbox [REQ-0002]
        - Language dropdown [REQ-0045]
        - Gmail credentials [REQ-0016]
        - Save/Cancel buttons [REQ-0047]
        """
        
    def load_current_settings(self) -> None:
        """Load current settings into form fields."""
        
    def apply_settings(self) -> None:
        """
        Validate and apply settings [REQ-0047].
        Save to settings manager.
        Emit signals for interval/language changes.
        """
        
    def cancel_settings(self) -> None:
        """Discard changes and close dialog [REQ-0047]."""
        
    def validate_inputs(self) -> Tuple[bool, List[str]]:
        """
        Validate input fields.
        Returns: (is_valid, error_messages)
        """
```

#### `app/ui/database_editor.py` - Contact Management
```python
class DatabaseEditor(QDialog):
    """
    Contact database editor dialog.
    
    Requirements: REQ-0011, REQ-0049
    """
    
    # Signals
    contact_added = pyqtSignal(Contact)
    contact_updated = pyqtSignal(Contact)
    contact_deleted = pyqtSignal(str)
    
    def __init__(self, contact_db: 'ContactDatabaseManager',
                 validator: 'DataValidator',
                 parent=None):
        """Initialize database editor [REQ-0049]."""
        super().__init__(parent)
        
    def setup_ui(self) -> None:
        """
        Create editor interface [REQ-0049].
        
        Components:
        - Contact list view
        - Add/Edit/Delete buttons
        - Contact form fields [REQ-0029]
        - Save/Cancel buttons
        """
        
    def show_contact_form(self, contact: Optional[Contact] = None) -> None:
        """
        Display contact form for add/edit [REQ-0049].
        Show validation messages [REQ-0049].
        """
        
    def add_contact(self) -> None:
        """Open form for new contact [REQ-0011, REQ-0017]."""
        
    def edit_contact(self, contact_id: str) -> None:
        """Open form to edit contact [REQ-0011, REQ-0017]."""
        
    def delete_contact(self, contact_id: str) -> None:
        """
        Delete contact with confirmation [REQ-0011, REQ-0017].
        Show visual feedback [REQ-0049].
        """
        
    def refresh_list(self) -> None:
        """Reload and display contacts list [REQ-0011]."""
        
    def apply_validation(self, errors: List[str]) -> None:
        """
        Display validation errors [REQ-0049].
        Highlight invalid fields.
        """
```

#### `app/ui/query_dialog.py` - Nameday Search
```python
class QueryDialog(QDialog):
    """
    Dialog for searching nameday information.
    
    Requirements: REQ-0013, REQ-0050
    """
    
    def __init__(self, nameday_ref: 'NamedayReferenceManager',
                 parent=None):
        """Initialize query dialog [REQ-0050]."""
        super().__init__(parent)
        
    def setup_ui(self) -> None:
        """
        Create query dialog layout [REQ-0050].
        
        Components:
        - Text input field for name [REQ-0050]
        - "Query" button to trigger search [REQ-0050]
        - "Exit" button to close [REQ-0050]
        - Results display area [REQ-0050]
        """
        
    def perform_query(self, name: str) -> None:
        """
        Search for nameday [REQ-0013, REQ-0050].
        Case handling per language [REQ-0013].
        Display results [REQ-0050].
        """
        
    def display_result(self, nameday: Optional[Nameday]) -> None:
        """Display search result to user [REQ-0050]."""
```

#### `app/ui/today_namedays_view.py` - Today's Namedays
```python
class TodayNamedaysView(QDialog):
    """
    Display all registered names with namedays today.
    
    Requirements: REQ-0012
    """
    
    def __init__(self, contact_db: 'ContactDatabaseManager',
                 parent=None):
        """Initialize today's namedays view [REQ-0012]."""
        super().__init__(parent)
        
    def setup_ui(self) -> None:
        """
        Create view layout [REQ-0012].
        Display complete list of today's namedays [REQ-0012].
        """
        
    def refresh_display(self) -> None:
        """
        Update display in real-time [REQ-0012].
        Query today's namedays and display.
        """
        
    def get_todays_namedays(self) -> List[Contact]:
        """
        Find all contacts with namedays today [REQ-0012].
        Returns: List of Contact objects.
        """
```

### 3.3 Internationalization Classes

#### `app/i18n/i18n_manager.py` - Language Support
```python
class I18nManager(QObject):
    """
    Manage multilingual UI strings.
    
    Requirements: REQ-0045, REQ-0046
    """
    
    # Signals
    language_changed = pyqtSignal(str)
    
    def __init__(self, default_language: str = "en"):
        """
        Initialize i18n manager [REQ-0046].
        Default language: English.
        """
        super().__init__()
        
    def set_language(self, language_code: str) -> None:
        """
        Set active language [REQ-0045].
        Update UI immediately [REQ-0045].
        Available languages: en, hu.
        """
        
    def get_string(self, key: str) -> str:
        """
        Get translated string by key [REQ-0046].
        Fallback to default language if not found.
        """
        
    def get_available_languages(self) -> List[str]:
        """
        Get list of available languages [REQ-0045, REQ-0046].
        Returns: Language codes (e.g., ['en', 'hu']).
        """
        
    def load_language_file(self, language_code: str) -> Dict[str, str]:
        """
        Load translation file [REQ-0046].
        JSON format with externalized strings.
        """
        
    def _validate_key(self, key: str) -> bool:
        """Validate string key exists in current language."""
```

---

## 4. Technology Stack Details

### PyQt5 Components Used
```python
QApplication          # Main application [REQ-0041]
QDialog               # Modal dialogs [REQ-0005, REQ-0047, REQ-0050]
QSystemTrayIcon       # System tray [REQ-0010, REQ-0042]
QMenu, QAction        # Context menu [REQ-0010]
QThread               # Background monitoring [REQ-0022]
QTimer                # Interval management [REQ-0003]
QLineEdit, QSpinBox, QComboBox  # Settings input [REQ-0047]
QTableWidget          # Contact list display [REQ-0011, REQ-0049]
QMessageBox           # Error/warning dialogs [REQ-0027]
QLabel, QVBoxLayout, QHBoxLayout  # UI layout
```

### Python Libraries Usage
```python
csv                   # CSV file operations [REQ-0037, REQ-0039]
json                  # Configuration storage [REQ-0055]
datetime              # Date/time handling [REQ-0023]
smtplib               # SMTP email [REQ-0052]
winreg                # Windows registry [REQ-0051]
pathlib               # Path operations
logging               # Application logging [REQ-0027]
threading             # Background tasks [REQ-0022]
re                    # Regex for validation [REQ-0040]
email.mime            # Email formatting [REQ-0052]
```

---

## 5. Step-by-Step Implementation Plan

### Phase 1: Foundation & Core Infrastructure (Week 1)

**Objective:** Establish project structure and core utilities.

#### Step 1.1: Project Setup
```
1. Create directory structure
2. Initialize git repository
3. Create requirements.txt with dependencies
4. Create setup.py for package installation
5. Create initial README.md
```
**REQ Mapping:** None (infrastructure)

#### Step 1.2: Exception & Type Definitions
**File:** `app/exceptions.py`, `app/types.py`, `app/constants.py`
```python
# app/exceptions.py
class NameDaysException(Exception): pass
class InvalidDateFormatError(NameDaysException): pass
class InvalidEmailError(NameDaysException): pass
class DatabaseError(NameDaysException): pass
class ConfigurationError(NameDaysException): pass

# app/types.py
from typing import NewType
ContactID = NewType('ContactID', str)
NamedayDate = NewType('NamedayDate', str)  # MM-DD format

# app/constants.py
DEFAULT_CHECK_INTERVAL = 15  # minutes [REQ-0003]
DEFAULT_LANGUAGE = "en"  # [REQ-0045]
NAMEDAY_DATE_FORMAT = "%m-%d"  # MM-DD [REQ-0023]
MAX_MEMORY_MB = 100  # [REQ-0024]
SUPPORTED_LANGUAGES = ["en", "hu"]  # [REQ-0045]
```
**REQ Mapping:** REQ-0023, REQ-0024, REQ-0045

#### Step 1.3: Utility Modules
**Files:** `app/utils/logger.py`, `app/utils/date_utils.py`, `app/utils/error_handler.py`
```python
# app/utils/logger.py
class AppLogger:
    """Logging utility for application [REQ-0027]."""
    def setup_logging(self) -> None: pass
    def get_logger(self, name: str): pass

# app/utils/date_utils.py
class DateUtils:
    """Date utility functions for MM-DD format [REQ-0023]."""
    @staticmethod
    def get_today_mmdd() -> str:
        """Return today's date in MM-DD format [REQ-0023]."""
    
    @staticmethod
    def is_valid_mmdd(date_str: str) -> bool:
        """Check MM-DD format validity [REQ-0023, REQ-0040]."""

# app/utils/error_handler.py
class ErrorHandler:
    """Graceful error handling [REQ-0027]."""
    @staticmethod
    def handle_database_error(error: Exception) -> None: pass
    @staticmethod
    def handle_email_error(error: Exception) -> None: pass
    @staticmethod
    def show_user_error(title: str, message: str) -> None: pass
```
**REQ Mapping:** REQ-0023, REQ-0027, REQ-0040

---

### Phase 2: Data Management (Week 2)

**Objective:** Implement database and configuration management.

#### Step 2.1: Data Validator
**File:** `app/services/data_validator.py`
```python
# Implement DataValidator class
class DataValidator:
    def validate_contact(self, contact: Contact) -> List[str]: pass
    def validate_nameday_date(self, date: str) -> bool: pass
    def validate_email(self, email: str) -> bool: pass
    def validate_name(self, name: str) -> bool: pass
    def validate_recipient(self, recipient: str) -> bool: pass
```
**Tests:** `tests/test_data_validator.py`
**REQ Mapping:** REQ-0030, REQ-0031, REQ-0032, REQ-0033, REQ-0034, REQ-0040

#### Step 2.2: Contact Database Manager
**File:** `app/managers/contact_db_manager.py`
```python
class Contact: pass  # Data class [REQ-0029]
class ContactDatabaseManager: pass  # CRUD operations [REQ-0017]

# Implement methods:
# - create_contact() [REQ-0017]
# - read_contacts() [REQ-0017, REQ-0021]
# - update_contact() [REQ-0017]
# - delete_contact() [REQ-0017]
# - CSV handling with UTF-8, semicolon [REQ-0037]
```
**Tests:** `tests/test_contact_db_manager.py`
**REQ Mapping:** REQ-0017, REQ-0021, REQ-0029, REQ-0030-0037, REQ-0040

#### Step 2.3: Nameday Reference Manager
**File:** `app/managers/nameday_reference_manager.py`
```python
class Nameday: pass  # Data class [REQ-0038]
class NamedayReferenceManager: pass  # Lookup [REQ-0018]

# Implement methods:
# - get_nameday() [REQ-0018]
# - get_names_for_date() [REQ-0023]
# - Load built-in reference [REQ-0039]
# - Support Hungarian names [REQ-0018]
```
**Tests:** `tests/test_nameday_reference_manager.py`
**Create:** `resources/namedays.csv` with minimum names [REQ-0018]:
```csv
name;main_nameday;other_nameday
János;06-04;11-30
Mária;05-01;08-15
Andrea;11-30;06-22
Adél;12-24;
```
**REQ Mapping:** REQ-0013, REQ-0018, REQ-0023, REQ-0038, REQ-0039

#### Step 2.4: Settings Manager
**File:** `app/managers/settings_manager.py`
```python
class Settings: pass  # Data class
class SettingsManager(QObject): pass  # Settings management

# Implement methods:
# - load_settings() [REQ-0026, REQ-0028]
# - save_settings() [REQ-0026]
# - Default fallback [REQ-0028]
# - JSON config file [REQ-0055]
```
**Tests:** `tests/test_settings_manager.py`
**REQ Mapping:** REQ-0014, REQ-0026, REQ-0028, REQ-0055

---

### Phase 3: Service Layer (Week 3)

**Objective:** Implement external service integrations.

#### Step 3.1: Email Service
**File:** `app/services/email_service.py`
```python
class EmailService: pass

# Implement methods:
# - send_email() [REQ-0007, REQ-0016, REQ-0019, REQ-0020]
# - authenticate() with Gmail [REQ-0016, REQ-0052]
# - validate_email_address() [REQ-0040]
# - Template support [REQ-0020]
# - Graceful failure handling [REQ-0027]
```
**Tests:** `tests/test_email_service.py` (mock SMTP)
**REQ Mapping:** REQ-0007, REQ-0016, REQ-0019, REQ-0020, REQ-0027, REQ-0040, REQ-0052

#### Step 3.2: Windows Startup Manager
**File:** `app/services/windows_startup.py`
```python
class WindowsStartupManager: pass

# Implement methods:
# - enable_auto_launch() [REQ-0002, REQ-0051]
# - disable_auto_launch() [REQ-0002, REQ-0051]
# - is_auto_launch_enabled() [REQ-0002]
# - is_running_at_startup() [REQ-0002]
# - Registry operations [REQ-0051]
# - Windows 10/11 compatible [REQ-0025]
```
**Tests:** `tests/test_windows_startup.py` (mock registry)
**REQ Mapping:** REQ-0002, REQ-0025, REQ-0051

---

### Phase 4: Core Engine (Week 4)

**Objective:** Implement background monitoring and notification system.

#### Step 4.1: Notification Queue & Data Classes
**File:** `app/core/notification_queue.py`
```python
class Notification: pass  # Data class
class NotificationQueue: pass  # Queue management
```
**REQ Mapping:** REQ-0004

#### Step 4.2: Monitoring Engine
**File:** `app/core/monitoring_engine.py`
```python
class MonitoringEngine(QThread): pass

# Implement methods:
# - Background thread [REQ-0022]
# - Check interval loop [REQ-0003]
# - check_namedays() [REQ-0004, REQ-0018, REQ-0023]
# - Support multiple same-day namedays [REQ-0004]
# - Resource efficient [REQ-0024]
```
**Tests:** `tests/test_monitoring_engine.py`
**REQ Mapping:** REQ-0003, REQ-0004, REQ-0018, REQ-0022, REQ-0023, REQ-0024

#### Step 4.3: Notification Manager
**File:** `app/core/notification_manager.py`
```python
class NotificationManager(QObject): pass

# Implement methods:
# - queue_notification() [REQ-0004]
# - show_notification() [REQ-0005]
# - handle_later_button() [REQ-0006]
# - handle_mail_button() [REQ-0007]
# - handle_done_button() [REQ-0008]
```
**Tests:** `tests/test_notification_manager.py`
**REQ Mapping:** REQ-0005, REQ-0006, REQ-0007, REQ-0008, REQ-0009, REQ-0019

---

### Phase 5: User Interface (Week 5)

**Objective:** Implement complete UI with all dialogs.

#### Step 5.1: Internationalization
**File:** `app/i18n/i18n_manager.py` and language JSON files
```python
class I18nManager(QObject): pass

# Language files:
# - app/i18n/en.json [REQ-0045, REQ-0046]
# - app/i18n/hu.json [REQ-0045, REQ-0046]

# String externalization for all UI [REQ-0046]
```
**REQ Mapping:** REQ-0045, REQ-0046

#### Step 5.2: System Tray
**File:** `app/ui/system_tray.py`
```python
class SystemTrayManager(QObject): pass

# Implement:
# - System tray icon [REQ-0010, REQ-0042]
# - Context menu [REQ-0010]
# - Menu items for: Show All [REQ-0012], Query [REQ-0013],
#   Settings [REQ-0014], Edit DB [REQ-0011], Exit [REQ-0015]
```
**REQ Mapping:** REQ-0010, REQ-0011, REQ-0012, REQ-0013, REQ-0014, REQ-0015, REQ-0042

#### Step 5.3: Notification Modal
**File:** `app/ui/notification_modal.py`
```python
class NotificationModal(QDialog): pass

# Implement:
# - Modal dialog [REQ-0005]
# - Display layout [REQ-0043]
# - Three buttons: Later, Mail, Done [REQ-0044]
# - Focused and blocking [REQ-0005]
# - Important connections list [REQ-0009]
```
**Tests:** `tests/test_ui_components.py`
**REQ Mapping:** REQ-0005, REQ-0006, REQ-0007, REQ-0008, REQ-0009, REQ-0043, REQ-0044

#### Step 5.4: Settings Dialog
**File:** `app/ui/settings_dialog.py`
```python
class SettingsDialog(QDialog): pass

# Implement:
# - Settings form [REQ-0047]
# - Check interval [REQ-0003]
# - Auto-launch toggle [REQ-0002]
# - Language selection [REQ-0045]
# - Gmail credentials [REQ-0016]
# - Save/Cancel buttons [REQ-0047]
```
**REQ Mapping:** REQ-0002, REQ-0003, REQ-0014, REQ-0016, REQ-0026, REQ-0045, REQ-0047

#### Step 5.5: Database Editor
**File:** `app/ui/database_editor.py`
```python
class DatabaseEditor(QDialog): pass

# Implement:
# - Contact form [REQ-0049]
# - Add/Edit/Delete operations [REQ-0011, REQ-0017]
# - Validation feedback [REQ-0049]
# - Contact list [REQ-0011]
```
**REQ Mapping:** REQ-0011, REQ-0017, REQ-0029-0040, REQ-0049

#### Step 5.6: Query Dialog
**File:** `app/ui/query_dialog.py`
```python
class QueryDialog(QDialog): pass

# Implement:
# - Text input [REQ-0050]
# - Query button [REQ-0050]
# - Exit button [REQ-0050]
# - Results display [REQ-0013, REQ-0050]
```
**REQ Mapping:** REQ-0013, REQ-0050

#### Step 5.7: Today's Namedays View
**File:** `app/ui/today_namedays_view.py`
```python
class TodayNamedaysView(QDialog): pass

# Implement:
# - Display today's namedays [REQ-0012]
# - Real-time updates [REQ-0012]
```
**REQ Mapping:** REQ-0012

---

### Phase 6: Application Integration (Week 6)

**Objective:** Integrate all components into working application.

#### Step 6.1: Main Application Class
**File:** `app/main.py`
```python
class NameDaysMonitoringApp(QApplication): pass

# Implement:
# - Application initialization [REQ-0001]
# - Manager setup
# - Auto-launch detection [REQ-0002]
# - Monitoring engine start [REQ-0022]
# - Graceful shutdown [REQ-0015]
# - PyQt5 integration [REQ-0041]
```
**REQ Mapping:** REQ-0001, REQ-0002, REQ-0015, REQ-0022, REQ-0041

#### Step 6.2: Entry Point
**File:** `main.py`
```python
# Main entry point script
if __name__ == "__main__":
    app = NameDaysMonitoringApp()
    sys.exit(app.run())
```

#### Step 6.3: Signal/Slot Connections
```
# Connect all component signals:
# - Monitoring engine -> notification manager
# - Notification buttons -> managers
# - Settings changes -> monitoring engine
# - Language changes -> all UI components
# - System tray menu -> dialogs
```

---

### Phase 7: Testing & Optimization (Week 7)

**Objective:** Comprehensive testing and performance optimization.

#### Step 7.1: Unit Testing
```
tests/
├── test_data_validator.py
├── test_contact_db_manager.py
├── test_nameday_reference_manager.py
├── test_settings_manager.py
├── test_email_service.py
├── test_windows_startup.py
├── test_monitoring_engine.py
├── test_notification_manager.py
└── test_ui_components.py
```
**Target:** >80% code coverage

#### Step 7.2: Integration Testing
```python
# Test full workflows:
# - Startup sequence
# - Notification display & interactions
# - Settings persistence
# - Database operations
# - Email sending
```

#### Step 7.3: Performance Testing
```python
# Verify [REQ-0024]:
# - Memory footprint < 100MB
# - CPU ~0% at rest
# - Interval accuracy
```

#### Step 7.4: Windows Compatibility Testing
```python
# Test on Windows 10/11 [REQ-0025]
# - Registry operations
# - System tray integration
# - Auto-launch functionality
```

---

### Phase 8: Documentation & Deployment (Week 8)

**Objective:** Complete documentation and prepare for release.

#### Step 8.1: Documentation
```
docs/
├── system_design.md        ✓ (completed)
├── architecture_diagram.svg ✓ (completed)
├── implementation.md        (this file)
├── API.md                   (auto-generated from docstrings)
└── SETUP.md                 (installation guide)
```

#### Step 8.2: Code Documentation
```python
# Every class/method has docstring:
# - Description
# - Parameters with types
# - Return types
# - Requirements (REQ IDs)
# - Examples where applicable
```

#### Step 8.3: Build & Package
```
1. Create setup.py for package installation
2. Create executable with PyInstaller
3. Create installer (.exe) with NSIS
4. Create deployment guide
```

#### Step 8.4: Release Checklist
```
- [ ] All 55 requirements implemented
- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] Performance targets met [REQ-0024]
- [ ] Windows 10/11 tested [REQ-0025]
- [ ] Code coverage >80%
- [ ] All docstrings complete
- [ ] User guide written
- [ ] Executable created
- [ ] Installer tested
```

---

## 6. Implementation Dependencies & Order

### Critical Path
```
1. Data Layer (Phase 2)
   ├─ DataValidator
   ├─ Contact DB Manager
   ├─ Nameday Reference Manager
   └─ Settings Manager

2. Service Layer (Phase 3)
   ├─ Email Service
   └─ Windows Startup Manager

3. Core Engine (Phase 4)
   ├─ Monitoring Engine
   └─ Notification Manager

4. UI Layer (Phase 5)
   ├─ I18n Manager
   ├─ System Tray
   ├─ Dialogs (all)
   └─ Modal Dialog

5. Integration (Phase 6)
   ├─ Main Application
   └─ Signal/Slot Wiring

6. Testing (Phase 7)
   ├─ Unit Tests
   ├─ Integration Tests
   └─ Performance Tests

7. Deployment (Phase 8)
   ├─ Documentation
   ├─ Packaging
   └─ Release
```

### Blocking Dependencies
```
Contact DB Manager ◄─── Notification Manager
         ▲                      ▲
         │                      │
         ├─ Database Editor ────┤
         │                      │
         └─ Monitoring Engine ──┘

Settings Manager ◄─── All Components
Email Service ◄─── Notification Manager
Windows Startup ◄─── Settings Dialog
I18n Manager ◄─── All UI Components
```

---

## 7. Code Style & Documentation Standards

### Naming Conventions
```python
# Classes: PascalCase
class ContactDatabaseManager: pass
class NotificationModal(QDialog): pass

# Functions/Methods: snake_case [REQ requirement]
def validate_contact(contact: Contact) -> List[str]: pass
def check_namedays(self) -> List[Notification]: pass

# Constants: UPPER_SNAKE_CASE
DEFAULT_CHECK_INTERVAL = 15
NAMEDAY_DATE_FORMAT = "%m-%d"

# Private members: _leading_underscore
def _load_csv(self) -> List[Contact]: pass
self._settings_manager: SettingsManager = ...
```

### Docstring Format
```python
def example_method(self, param1: str, param2: int) -> bool:
    """
    Short description on first line.
    
    Longer description if needed with more details about
    what the method does and how it works.
    
    Args:
        param1: Description of first parameter
        param2: Description of second parameter
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When something is invalid
    
    Requirements: REQ-0001, REQ-0002
    Note: Any special notes or caveats
    
    Example:
        >>> method = ExampleClass()
        >>> result = method.example_method("test", 42)
        >>> assert result is True
    """
    pass
```

### Type Hints
```python
# Always use type hints
def create_contact(self, contact: Contact) -> None: pass
def get_contacts(self) -> List[Contact]: pass
def find_contact(self, name: str) -> Optional[Contact]: pass

# Use imports for complex types
from typing import List, Dict, Optional, Tuple, Union
from pathlib import Path

contact_list: List[Contact] = []
settings_dict: Dict[str, Any] = {}
maybe_contact: Optional[Contact] = None
```

### Inline Documentation Expectations
```python
# Every class has module-level docstring
# Every public method has docstring with REQ IDs
# Complex logic has inline comments explaining why
# Magic numbers are explained or extracted as constants

# Example:
class MonitoringEngine(QThread):
    """
    Background thread for monitoring namedays [REQ-0022].
    
    Checks for today's namedays at configurable intervals [REQ-0003]
    and emits signals to display notifications [REQ-0005].
    """
    
    def check_namedays(self) -> List[Notification]:
        """
        Query databases for today's namedays [REQ-0023].
        
        Returns all contacts with nameday today, supporting
        multiple namedays on same day [REQ-0004].
        """
        # Get today's date in MM-DD format [REQ-0023]
        today = DateUtils.get_today_mmdd()
        
        # Query nameday reference database [REQ-0018]
        nameday_names = self._nameday_ref.get_names_for_date(today)
        
        # Find matching contacts [REQ-0017]
        contacts = self._contact_db.get_contacts_by_nameday(today)
        
        # Build notifications, one per contact [REQ-0004]
        notifications = [
            Notification(contact=contact, nameday_date=today)
            for contact in contacts
        ]
        
        return notifications
```

---

## 8. Testing Strategy

### Unit Testing Philosophy
```python
# Test each class/function independently
# Mock external dependencies (DB, email, registry)
# Test happy path and error cases
# Aim for >80% coverage

class TestContactDatabaseManager:
    """Test contact CRUD operations [REQ-0017]."""
    
    def test_create_contact_valid(self):
        """Valid contact should be created [REQ-0017]."""
        
    def test_create_contact_invalid_email(self):
        """Invalid email should be rejected [REQ-0040]."""
        
    def test_get_contact_by_nameday(self):
        """Should find contacts by date [REQ-0023]."""
        
    def test_csv_semicolon_delimiter(self):
        """CSV should use semicolon delimiter [REQ-0037]."""
```

### Integration Testing
```python
# Test component interactions
# Full startup sequence
# Notification workflow (display -> action -> done)
# Settings changes affecting other components
# Email sending via manager chain
```

### Performance Testing
```python
# Memory profiling [REQ-0024]
# CPU profiling at rest [REQ-0024]
# Interval accuracy [REQ-0003]
# CSV parsing performance with large files
```

---

## 9. REQ ID to Implementation Mapping Summary

| REQ ID | Component | Phase | Status |
|--------|-----------|-------|--------|
| REQ-0001 | NameDaysMonitoringApp.\_\_init\_\_ | 6 | Entry point |
| REQ-0002 | WindowsStartupManager | 3 | Auto-launch |
| REQ-0003 | MonitoringEngine.set_interval | 4 | Interval mgmt |
| REQ-0004 | MonitoringEngine.check_namedays | 4 | Multi-name support |
| REQ-0005 | NotificationModal | 5 | UI modal |
| REQ-0006 | NotificationManager.handle_later | 4 | Reschedule |
| REQ-0007 | NotificationManager.handle_mail | 4 | Email trigger |
| REQ-0008 | NotificationManager.handle_done | 4 | Disable notifications |
| REQ-0009 | NotificationModal.setup_ui | 5 | Display layout |
| REQ-0010 | SystemTrayManager | 5 | Tray icon |
| REQ-0011 | DatabaseEditor | 5 | Contact management |
| REQ-0012 | TodayNamedaysView | 5 | Show today's names |
| REQ-0013 | QueryDialog | 5 | Nameday search |
| REQ-0014 | SettingsDialog | 5 | Settings access |
| REQ-0015 | NameDaysMonitoringApp.cleanup | 6 | Graceful exit |
| REQ-0016 | EmailService | 3 | Gmail integration |
| REQ-0017 | ContactDatabaseManager | 2 | CRUD operations |
| REQ-0018 | NamedayReferenceManager | 2 | Nameday lookup |
| REQ-0019 | EmailService.send_email | 3 | User-triggered email |
| REQ-0020 | EmailService._apply_template | 3 | Email templates |
| REQ-0021 | ContactDatabaseManager.read_contacts | 2 | Data persistence |
| REQ-0022 | MonitoringEngine | 4 | Background monitoring |
| REQ-0023 | DateUtils.get_today_mmdd | 1 | Date format |
| REQ-0024 | MonitoringEngine (threading) | 4 | Resource efficiency |
| REQ-0025 | WindowsStartupManager | 3 | Windows only |
| REQ-0026 | SettingsManager | 2 | Settings persistence |
| REQ-0027 | ErrorHandler | 1 | Error handling |
| REQ-0028 | SettingsManager.reset_to_defaults | 2 | Config recovery |
| REQ-0029 | Contact class | 2 | Record fields |
| REQ-0030 | DataValidator.validate_name | 2 | Name validation |
| REQ-0031 | DataValidator.validate_nameday_date | 2 | Date validation |
| REQ-0032 | Contact.other_nameday | 2 | Optional date |
| REQ-0033 | DataValidator.validate_recipient | 2 | Recipient validation |
| REQ-0034 | DataValidator.validate_email | 2 | Email validation |
| REQ-0035 | Contact.prewritten_email | 2 | Email template |
| REQ-0036 | Contact.comment | 2 | Comment field |
| REQ-0037 | ContactDatabaseManager._load_csv | 2 | CSV format |
| REQ-0038 | Nameday class | 2 | Reference fields |
| REQ-0039 | NamedayReferenceManager._load_reference | 2 | Reference CSV |
| REQ-0040 | DataValidator | 2 | Data validation |
| REQ-0041 | NameDaysMonitoringApp | 6 | PyQt5 framework |
| REQ-0042 | SystemTrayManager | 5 | Tray integration |
| REQ-0043 | NotificationModal.setup_ui | 5 | Modal layout |
| REQ-0044 | NotificationModal.setup_buttons | 5 | Button arrangement |
| REQ-0045 | I18nManager.set_language | 5 | Language selection |
| REQ-0046 | I18nManager.get_string | 5 | Multilingual UI |
| REQ-0047 | SettingsDialog | 5 | Settings dialog |
| REQ-0048 | NotificationModal.closeEvent | 5 | Dismissal |
| REQ-0049 | DatabaseEditor | 5 | Editor interface |
| REQ-0050 | QueryDialog | 5 | Query dialog |
| REQ-0051 | WindowsStartupManager (registry) | 3 | Startup integration |
| REQ-0052 | EmailService._send_smtp | 3 | SMTP integration |
| REQ-0053 | ContactDatabaseManager (CSV I/O) | 2 | CSV persistence |
| REQ-0054 | N/A | N/A | Optional (not implemented) |
| REQ-0055 | SettingsManager (config file) | 2 | Config storage |

---

## 10. Additional Implementation Notes

### Error Handling Strategy
```python
# Custom exceptions for domain errors [REQ-0027]
try:
    contact_db.create_contact(contact)
except ValidationError as e:
    # Handle validation - show to user
    ErrorHandler.show_user_error("Invalid Contact", str(e))
except DatabaseError as e:
    # Handle DB error - log and inform user
    logger.error(f"Database error: {e}")
    ErrorHandler.show_user_error("Database Error", "Failed to save contact")
except Exception as e:
    # Unexpected error - log and handle gracefully
    logger.exception(f"Unexpected error: {e}")
    ErrorHandler.show_user_error("Error", "An unexpected error occurred")
```

### Configuration File Example
```json
{
  "check_interval": 15,
  "auto_launch": false,
  "language": "en",
  "gmail_account": "",
  "gmail_password": "",
  "notifications_enabled": true
}
```

### CSV File Examples

**contacts.csv** [REQ-0037]
```csv
name;main_nameday;other_nameday;recipient;email_addresses;prewritten_email;comment
János Kovács;06-04;11-30;János (work);janos@example.com;Dear János,\nHappy nameday!;Colleague from IT
Mária Kiss;05-01;08-15;Mária;maria@example.com;;Manager
```

**namedays.csv** [REQ-0039]
```csv
name;main_nameday;other_nameday
János;06-04;11-30
Mária;05-01;08-15
Andrea;11-30;06-22
Adél;12-24;
István;08-20;
```

### Logging Examples
```python
# app/utils/logger.py
logger.info("Application started [REQ-0001]")
logger.info(f"Monitoring interval changed to {minutes} minutes [REQ-0003]")
logger.warning(f"Failed to send email to {contact.name}: {error} [REQ-0027]")
logger.error(f"Database error while creating contact: {error} [REQ-0027]")
logger.exception(f"Unexpected error: {error} [REQ-0027]")
```

---

## Document Control
**Version:** 1.0  
**Date:** 2026-03-30  
**Status:** Final Implementation Plan  
**Total Phases:** 8 weeks  
**Total Classes:** 25+  
**Total Requirements Mapped:** 55/55  
**Expected LOC:** 5,000-7,000 lines
