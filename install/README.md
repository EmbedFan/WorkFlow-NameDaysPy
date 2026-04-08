# Name Days Monitoring App

A Windows desktop application for monitoring contact namedays and delivering timely notifications.

## Overview

The Name Days Monitoring App runs in the background and periodically checks for upcoming namedays among your contacts. When a nameday is found, the application displays a modal notification with options to send a greeting email, defer the notification, or mark the contact as done.

**Key Features:**
- ✓ Background monitoring (configurable interval)
- ✓ System tray integration
- ✓ Email notifications via Gmail SMTP
- ✓ Contact database management (CSV-based)
- ✓ Nameday reference database (built-in)
- ✓ Auto-launch at Windows startup (optional)
- ✓ Multi-language support (English, Hungarian)
- ✓ Low-resource implementation (<100MB memory)

## System Requirements

- **OS:** Windows 7 or later
- **Python:** 3.7 or higher
- **RAM:** 100MB minimum
- **Disk Space:** 50MB

## Installation

1. **Clone or download the project:**
   ```bash
   cd WorkFlow-NameDaysPy
   ```

2. **Create virtual environment (recommended):**
   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Generate sample data:**
   ```bash
   python resources/generate_namedays.py
   ```

## Usage

### Starting the Application

**Option 1: Direct execution**
```bash
python main.py
```

**Option 2: Via Python**
```bash
python -m app.main
```

**Option 3: Installed package**
```bash
namedays-app
```

### Configuration

Configuration is stored in `config/config.json`. Key settings:

- **check_interval**: Minutes between nameday checks (1-1440, default: 15)
- **auto_launch**: Enable auto-start with Windows (true/false)
- **language**: Application language ("en" or "hu")
- **gmail_account**: Gmail email for sending notifications
- **gmail_password**: Gmail password or app token
- **notifications_enabled**: Global notification toggle

### Adding Contacts

Contacts are stored in `data/contacts.csv` with the following fields:

| Field | Description | Example |
|-------|-------------|---------|
| name | Contact's full name | John Smith |
| main_nameday | Primary nameday (MM-DD) | 03-14 |
| other_nameday | Secondary nameday (MM-DD) | 10-25 |
| recipient | Recipient label | Friend |
| email_addresses | Email(s) separated by semicolon | john@example.com |
| prewritten_email | Email template (optional) |  |
| comment | Custom note (optional) |  |
| notification_disabled | Disable notifications (true/false) | false |

### Using Gmail Integration

To enable email notifications:

1. Use your Gmail account email and password, OR
2. Generate an [App Password](https://myaccount.google.com/apppasswords) if 2FA is enabled
3. Enter credentials in the Settings dialog
4. Test the connection

### Windows Startup Integration

To enable automatic application launch at Windows startup [REQ-0002, REQ-0051]:

**Using Settings Dialog:**
1. Open Settings from the system tray menu
2. Check the "Auto-launch at startup" option
3. The application will be registered in Windows registry
4. Next system restart will launch the app automatically

**Programmatic Control** (via `app/services/windows_startup.py`):

The `WindowsStartupManager` class provides methods to manage Windows registry entries for auto-launch:

```python
from app.services.windows_startup import WindowsStartupManager

#Initialize manager
manager = WindowsStartupManager()

# Enable auto-launch
manager.enable_auto_launch(r"C:\path\to\python main.py")

# Check if auto-launch is enabled
if manager.is_auto_launch_enabled():
   print("Application will auto-launch at startup")

# Disable auto-launch
manager.disable_auto_launch()

# Check if running at system startup
if manager.is_running_at_startup():
   print("Application was launched at system startup")
```

## Project Structure

```
WorkFlow-NameDaysPy/
├── app/                          # Main application package
│   ├── main.py                   # Application entry point
│   ├── constants.py              # Configuration constants
│   ├── types.py                  # Data classes (Contact, Notification, etc.)
│   ├── exceptions.py             # Custom exceptions
│   │
│   ├── core/                     # Core monitoring and notification
│   │   ├── monitoring_engine.py  # Background monitoring loop
│   │   ├── notification_manager.py  # Notification handling
│   │   └── notification_queue.py # Notification queue
│   │
│   ├── managers/                 # Data management
│   │   ├── contact_db_manager.py   # Contact CRUD operations
│   │   ├── nameday_reference_manager.py  # Nameday lookup
│   │   └── settings_manager.py   # Settings persistence
│   │
│   ├── services/                 # External services
│   │   ├── email_service.py      # Gmail integration
│   │   ├── windows_startup.py    # Auto-launch management
│   │   └── data_validator.py     # Input validation
│   │
│   ├── ui/                       # User interface
│   │   ├── system_tray.py        # System tray icon
│   │   ├── notification_modal.py # Notification dialog
│   │   └── (other UI components)
│   │
│   ├── i18n/                     # Internationalization
│   │   ├── en.json               # English strings
│   │   └── hu.json               # Hungarian strings
│   │
│   └── utils/                    # Utility modules
│       ├── logger.py             # Logging setup
│       ├── file_utils.py         # File operations
│       ├── date_utils.py         # Date utilities
│       └── error_handler.py      # Error handling
│
├── resources/                    # Application resources
│   ├── namedays.csv              # Nameday reference database
│   ├── app_icon.png              # System tray icon
│   ├── styles/                   # Qt stylesheets
│   │   └── default.qss
│   └── generate_namedays.py      # Sample data generator
│
├── config/                       # Configuration directory
│   └── config.json               # Application settings
│
├── data/                         # Data directory
│   └── contacts.csv              # Contact database
│
├── tests/                        # Unit tests
├── docs/                         # Documentation
├── requirements.txt              # Python dependencies
├── setup.py                      # Package setup
├── main.py                       # Entry point script
└── README.md                     # This file
```

## Requirements Mapping

This application implements the following requirements:

| Category | Requirements |
|----------|--------------|
| **Core** | REQ-0001 (Init), REQ-0002 (Auto-launch), REQ-0003 (Interval), REQ-0004 (Match names) |
| **UI** | REQ-0005 (Modal), REQ-0010 (Tray), REQ-0011-0015 (UI features) |
| **Notifications** | REQ-0006 (Later), REQ-0007 (Mail), REQ-0008 (Done), REQ-0009 (Queue) |
| **Data** | REQ-0017-0021 (Database), REQ-0023 (Date format), REQ-0026-0028 (Settings) |
| **Contact** | REQ-0029-0040 (Contact data) |
| **Integration** | REQ-0041 (PyQt5), REQ-0045-0046 (i18n), REQ-0051-0052 (Windows/Gmail) |

## Architecture

The application follows a layered architecture:

1. **UI Layer** - PyQt5 dialogs and system tray integration
2. **Core Logic** - Monitoring engine and notification manager  
3. **Data Access** - Database managers and settings persistence
4. **Services** - Email, Windows integration, validation
5. **Utilities** - Logging, file I/O, error handling

Key design patterns:
- **Thread-safe queuing** for notifications
- **Event-driven** notification handling
- **Configuration management** with defaults
- **Comprehensive error handling** and logging

## Development

### Running Tests

```bash
pytest tests/
pytest --cov=app tests/  # With coverage
```

### Code Quality

```bash
black app/        # Format code
pylint app/       # Lint code
```

### Building Distribution

```bash
python setup.py sdist bdist_wheel
```

## Troubleshooting

### App fails to start
- Check log file in `logs/` directory
- Verify Python 3.7+ is installed
- Ensure all dependencies are installed: `pip install -r requirements.txt`

### Notifications not showing
- Check `config/config.json` for settings
- Verify contacts exist in `data/contacts.csv`
- Check nameday dates are in MM-DD format
- Ensure notifications are not disabled for contact

### Email not sending
- Verify Gmail credentials in settings
- Check if Gmail 2FA is enabled (use App Password instead)
- Review error logs in `logs/` directory
- Test SMTP connection

### High memory usage
- Check monitoring interval (reduce for lower memory)
- Verify notification queue is being processed
- Review for memory leaks in logs

## Contributing

Contributions are welcome! Please:

1. Create a feature branch
2. Write tests for new functionality
3. Follow PEP 8 style guidelines
4. Submit a pull request

## License

MIT License - See LICENSE file for details

## Support

For issues and feature requests, please open an issue on the project repository.

## Changelog

### Version 1.0.0 (2026-03-30)
- Initial release
- Core monitoring and notification system
- Gmail integration
- Contact management
- System tray integration
- Multi-language support

---

## Notes for Developers

- The application runs as a daemon in the background
- Uses PyQt5 for UI and system tray integration
- Data is persisted in CSV files (UTF-8, semicolon-delimited)
- Configuration stored in JSON format
- Thread-safe notification queue for concurrent operations
- Comprehensive logging for debugging

For detailed implementation information, see the documentation in `docs/` folder.
