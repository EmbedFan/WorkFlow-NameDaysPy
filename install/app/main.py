"""
Main application entry point [REQ-0001, REQ-0002, REQ-0015, REQ-0041].

Initializes and runs the Name Days Monitoring Application.
"""

import sys
from pathlib import Path

from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtGui import QIcon

from app.managers import ContactDatabaseManager, NamedayReferenceManager, SettingsManager
from app.services import EmailService, WindowsStartupManager, DataValidator
from app.core import MonitoringEngine, NotificationQueue, NotificationManager
from app.ui.system_tray import SystemTrayIcon
from app.utils import setup_logging, get_logger
from app.constants import RESOURCES_DIR,  APP_NAME, CONTACTS_CSV_PATH, NAMEDAYS_CSV_PATH, CONFIG_JSON_PATH
from app.i18n.translator import install_translator

logger = setup_logging(APP_NAME)


class NameDaysMonitoringApp(QApplication):
    """
    Main application class [REQ-0001, REQ-0002, REQ-0015, REQ-0041].
    
    Initializes the application and manages lifecycle.
    - Initialize PyQt5 application [REQ-0041]
    - Create UI components (tray icon) [REQ-0010, REQ-0042]
    - Start background monitoring [REQ-0022]
    - Handle auto-launch [REQ-0002]
    - Graceful shutdown [REQ-0015]
    """
    
    def __init__(self, args=None):
        """
        Initialize application [REQ-0001, REQ-0041].
        
        Args:
            args: Command line arguments
        """
        if args is None:
            args = sys.argv

        super().__init__(args)

        # **CRITICAL**: Install translator before creating any UI components to ensure all text is translated correctly [REQ-0046]
        # Settings manager
        self.settings = SettingsManager(CONFIG_JSON_PATH)

        # Setup logging
        self.logger = logger  # Use the module-level logger with the file handler
        self.logger.info(f"Starting {APP_NAME}")

        # Load appropriate language translator [REQ-0046]
        user_language = self.settings.language  # "en" or "hu"
        install_translator(self, user_language)

        self.logger.info(f"Translated text 'Exit' is: {self.tr('Exit')} [REQ-0046]")  

        self.logger.info(f"Language self set to: {user_language} [REQ-0046]")
        # End of frozen section - all initialization code should be above this line to ensure proper setup before UI components are created
        

        # IMPORTANT: Prevent app from exiting when all windows are closed
        # This is essential for tray-only applications
        self.setQuitOnLastWindowClosed(False)
                
        # Initialize managers
        self._setup_managers()
        
        # Setup core components
        self._setup_core()
        
        # Setup UI
        self._setup_ui()
        
        # Check auto-launch [REQ-0002]
        self.detect_auto_launch()
        
        # Start monitoring [REQ-0022]
        self.start_monitoring()
    
    def _setup_managers(self):
        """Initialize all manager instances."""
        try:
            self.logger.info("Setting up managers...")
            
            # Data validator
            self.validator = DataValidator()
            
            # Database managers
            self.contact_db = ContactDatabaseManager(CONTACTS_CSV_PATH, self.validator)
            self.nameday_ref = NamedayReferenceManager(NAMEDAYS_CSV_PATH)            
            
            # Email service
            settings = self.settings.get_settings()
            self.email_service = EmailService(settings.gmail_account, settings.gmail_password)
            
            # Windows startup manager
            self.startup_manager = WindowsStartupManager()
            
            self.logger.info("Managers initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize managers: {e}")
            raise
    
    def _setup_core(self):
        """Setup core monitoring and notification components."""
        try:
            self.logger.info("Setting up core components...")
            
            # Notification queue
            self.notification_queue = NotificationQueue()
            
            # Notification manager
            self.notification_manager = NotificationManager(
                self.email_service,
                self.contact_db,
                self.notification_queue
            )
            
            # Monitoring engine
            settings = self.settings.get_settings()
            self.monitoring_engine = MonitoringEngine(
                self.contact_db,
                self.nameday_ref,
                self.notification_queue,
                settings.check_interval
            )
            
            self.logger.info("Core components initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize core components: {e}")
            raise
    
    def _setup_ui(self):
        """Create UI components (tray icon, hidden main window) [REQ-0010, REQ-0042]."""
        try:
            self.logger.info("Setting up UI...")
            
            # Create hidden main window as parent for dialogs
            self.main_window = QMainWindow()
            self.main_window.hide()  # Hide but keep it in memory for dialog parenting
            
            # System tray icon [REQ-0010, REQ-0042]
            self.tray_icon = SystemTrayIcon(
                self.settings,
                self.contact_db,
                self.nameday_ref,
                self.validator,  # Pass data validator for add/edit dialogs
                self.main_window  # Pass main window instead of app
            )
            self.tray_icon.show()
            
            self.logger.info("UI initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize UI: {e}")
            raise
    
    def setup_ui(self) -> None:
        """Create UI components. Already done in __init__."""
        pass
    
    def setup_managers(self) -> None:
        """Initialize all manager instances. Already done in __init__."""
        pass
    
    def start_monitoring(self) -> None:
        """Start background monitoring thread [REQ-0022]."""
        try:
            self.logger.info("Starting monitoring engine...")
            self.monitoring_engine.start()
            self.logger.info("Monitoring engine started")
        except Exception as e:
            self.logger.error(f"Failed to start monitoring: {e}")
    
    def detect_auto_launch(self) -> bool:
        """
        Detect if app started at Windows startup [REQ-0002].
        
        Returns:
            True if started at startup, False otherwise
        """
        is_startup = self.startup_manager.is_running_at_startup()
        if is_startup:
            self.logger.info("App started at Windows startup [REQ-0002]")
        return is_startup
    
    def cleanup(self) -> None:
        """
        Graceful shutdown [REQ-0015].
        
        Stops monitoring, saves state, and exits cleanly.
        """
        try:
            self.logger.info("Cleaning up...")
            
            # Stop monitoring
            if hasattr(self, 'monitoring_engine'):
                self.monitoring_engine.stop_monitoring()
            
            # Save settings
            if hasattr(self, 'settings'):
                self.settings.save_settings()
            
            self.logger.info("Cleanup complete. Shutting down.")
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
    
    def closeEvent(self, event):
        """Handle application close event [REQ-0015]."""
        self.cleanup()
        event.accept()


def main():
    """Entry point for application."""
    try:
        app = NameDaysMonitoringApp()
        sys.exit(app.exec_())
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
