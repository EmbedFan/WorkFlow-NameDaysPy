"""
Application-wide constants and configuration values.

Includes default settings, file paths, validation rules, and system constraints.
"""

from pathlib import Path

# Application Metadata
APP_NAME = "app"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Development Team"

# File Paths (relative to application root)
APP_ROOT = Path(__file__).parent.parent
CONFIG_DIR = APP_ROOT / "config"
RESOURCES_DIR = APP_ROOT / "resources"
DATA_DIR = APP_ROOT / "data"
LOGS_DIR = APP_ROOT / "logs"

# Data Files
CONTACTS_CSV_PATH = DATA_DIR / "contacts.csv"
NAMEDAYS_CSV_PATH = RESOURCES_DIR / "namedays.csv"
CONFIG_JSON_PATH = CONFIG_DIR / "config.json"

# Default Settings [REQ-0028]
DEFAULT_CHECK_INTERVAL_MINUTES = 15  # [REQ-0003]
DEFAULT_LANGUAGE = "en"  # [REQ-0045]
DEFAULT_AUTO_LAUNCH = False  # [REQ-0002]
DEFAULT_NOTIFICATIONS_ENABLED = True  # [REQ-0014]

# Check Interval Constraints
MIN_CHECK_INTERVAL = 1
MAX_CHECK_INTERVAL = 1440  # 24 hours

# CSV Format Specifications [REQ-0037, REQ-0039]
CSV_ENCODING = "utf-8"
CSV_DELIMITER = ";"
CONTACTS_CSV_HEADER = "name;main_nameday;other_nameday;recipient;email_addresses;prewritten_email;comment;notification_disabled"
NAMEDAYS_CSV_HEADER = "name;main_nameday;other_nameday"

# Date Format [REQ-0023]
NAMEDAY_DATE_FORMAT = "MM-DD"
NAMEDAY_DATE_PATTERN = r"^(0[1-9]|1[0-2])-(0[1-9]|[12][0-9]|3[01])$"

# Supported Languages [REQ-0045, REQ-0046]
SUPPORTED_LANGUAGES = ["en", "hu"]
LANGUAGE_NAMES = {
    "en": "English",
    "hu": "Magyar (Hungarian)"
}

# Email Validation
EMAIL_PATTERN = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

# Gmail Configuration [REQ-0016, REQ-0052]
GMAIL_SMTP_SERVER = "smtp.gmail.com"
GMAIL_SMTP_PORT = 587

# Windows Registry Paths [REQ-0051]
STARTUP_REGISTRY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
STARTUP_REGISTRY_KEY = APP_NAME

# UI Dimensions
NOTIFICATION_MODAL_WIDTH = 500
NOTIFICATION_MODAL_HEIGHT = 300
SETTINGS_DIALOG_WIDTH = 600
SETTINGS_DIALOG_HEIGHT = 400
DATABASE_EDITOR_WIDTH = 800
DATABASE_EDITOR_HEIGHT = 500
QUERY_DIALOG_WIDTH = 400
QUERY_DIALOG_HEIGHT = 300

# Modal Behavior [REQ-0005, REQ-0043, REQ-0044]
NOTIFICATION_MODAL_ALWAYS_ON_TOP = True
NOTIFICATION_MODAL_BLOCKING = True
NOTIFICATION_MODAL_TIMEOUT_SECONDS = 0  # No auto-close

# Memory Management [REQ-0024]
MAX_MEMORY_MB = 100  # Target <100MB

# Logging Configuration
LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_MAX_BYTES = 10485760  # 10MB
LOG_BACKUP_COUNT = 5

# Notification Queue Settings
MAX_NOTIFICATION_QUEUE_SIZE = 100

# Timeouts (seconds)
EMAIL_SEND_TIMEOUT = 30
DATABASE_OPERATION_TIMEOUT = 5

# Error Messages
ERROR_INVALID_EMAIL = "Invalid email address format"
ERROR_INVALID_DATE = "Invalid date format (expected MM-DD)"
ERROR_INVALID_NAME = "Name cannot be empty"
ERROR_INVALID_RECIPIENT = "Recipient label cannot be empty"
ERROR_DATABASE_LOAD = "Failed to load contact database"
ERROR_DATABASE_SAVE = "Failed to save contact database"
ERROR_INVALID_CONFIG = "Invalid configuration"
ERROR_EMAIL_SEND = "Failed to send email"

# Success Messages
SUCCESS_EMAIL_SENT = "Email sent successfully"
SUCCESS_CONTACT_CREATED = "Contact created successfully"
SUCCESS_CONTACT_UPDATED = "Contact updated successfully"
SUCCESS_CONTACT_DELETED = "Contact deleted successfully"
SUCCESS_NOTIFICATION_DISABLED = "Notifications disabled for contact"

# System Tray Menu Items [REQ-0010, REQ-0042]
TRAY_MENU_SETTINGS = "Settings"
TRAY_MENU_DATABASE = "Database"
TRAY_MENU_QUERY = "Query"
TRAY_MENU_TODAY = "Today's Namedays"
TRAY_MENU_SEPARATOR = "---"
TRAY_MENU_EXIT = "Exit"

# UI Button Labels [REQ-0044]
BUTTON_LATER = "Later"
BUTTON_MAIL = "Mail"
BUTTON_DONE = "Done"
BUTTON_OK = "OK"
BUTTON_CANCEL = "Cancel"
BUTTON_SAVE = "Save"
BUTTON_DELETE = "Delete"
BUTTON_ADD = "Add"
BUTTON_EDIT = "Edit"
BUTTON_SEARCH = "Search"
