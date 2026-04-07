"""
System tray icon and context menu [REQ-0010, REQ-0042].

Provides system tray integration for background app control.
"""

from PyQt5.QtWidgets import QSystemTrayIcon, QApplication, QMenu, QDialog
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QCoreApplication
from pathlib import Path

from app.utils import get_logger
from app.constants import (
    TRAY_MENU_SETTINGS, TRAY_MENU_DATABASE, TRAY_MENU_QUERY,
    TRAY_MENU_TODAY, TRAY_MENU_EXIT, RESOURCES_DIR
)

logger = get_logger(__name__)


class SystemTrayIcon(QSystemTrayIcon):
    """
    System tray icon and menu [REQ-0010, REQ-0042].
    
    Provides quick access to application features and settings.
    """
    
    def __init__(self, settings_manager, contact_db, nameday_ref, data_validator=None, main_window=None):
        """
        Initialize system tray icon [REQ-0010, REQ-0042].
        
        Args:
            settings_manager: SettingsManager instance
            contact_db: ContactDatabaseManager instance
            nameday_ref: NamedayReferenceManager instance
            data_validator: DataValidator instance for contact validation
            main_window: Hidden main window to serve as parent for dialogs
        """
        super().__init__()  # No parent for QSystemTrayIcon
        
        # Store managers and main window
        self.settings_manager = settings_manager
        self.contact_db = contact_db
        self.nameday_ref = nameday_ref
        self.data_validator = data_validator
        self.dialog_parent = main_window  # Store for dialog parenting
        
        # Try to load icon, fallback to default
        icon_path = RESOURCES_DIR / "app_icon.png"
        if icon_path.exists():
            self.setIcon(QIcon(str(icon_path)))
        else:
            # Fallback icon
            self.setIcon(QApplication.style().standardIcon(0))
        
        # Create context menu
        self.menu = QMenu()
        self._setup_menu()
        self.setContextMenu(self.menu)
        
        logger.info("System tray icon initialized")
    
    def _setup_menu(self):
        """Setup system tray context menu with icons [REQ-0010]."""
        settings_action = self.menu.addAction(self._load_icon("settings.png"), self.tr("Settings"))
        settings_action.triggered.connect(self._on_settings)
        
        database_action = self.menu.addAction(self._load_icon("database.png"), self.tr("Database"))
        database_action.triggered.connect(self._on_database)
        
        query_action = self.menu.addAction(self._load_icon("query.png"), self.tr("Query"))
        query_action.triggered.connect(self._on_query)
        
        today_action = self.menu.addAction(self._load_icon("today.png"), self.tr("Today's Namedays"))
        today_action.triggered.connect(self._on_today)
        
        # Separator before reload
        self.menu.addSeparator()
        
        # Reload Namedays Database action [REQ-0066]
        reload_action = self.menu.addAction(self.tr("Reload Namedays Database"))
        reload_action.triggered.connect(self._on_reload_namedays)
        
        # Separator
        self.menu.addSeparator()
        
        # Exit action
        exit_action = self.menu.addAction(self._load_icon("exit.png"), QCoreApplication.translate("SystemTrayIcon", "Exit"))
        exit_action.triggered.connect(self._on_exit)
        
        logger.info("System tray menu setup complete with actions: Settings, Database, Query, Today's Namedays, Exit")
        logger.info(f"Menu name for exit translated to: {self.tr("Exit")}")
    
    def _load_icon(self, filename: str) -> QIcon:
        """Load icon from resources directory."""
        icon_path = RESOURCES_DIR / filename
        if icon_path.exists():
            return QIcon(str(icon_path))
        return QIcon()  # Empty fallback
    
    def show_message(self, title: str, message: str, duration: int = 10000):
        """
        Show tray notification message.
        
        Args:
            title: Message title
            message: Message text
            duration: Display duration in milliseconds
        """
        self.showMessage(title, message, msecs=duration)
    
    def _on_settings(self):
        """Handle Settings menu action."""
        logger.info("Settings action triggered")
        from app.ui.settings_dialog import SettingsDialog
        dialog = SettingsDialog(self.settings_manager, self.dialog_parent)
        dialog.exec_()

    def _on_database(self):
        """Handle Database menu action."""
        logger.info("Database action triggered")
        from app.ui.database_editor_dialog import DatabaseEditorDialog
        dialog = DatabaseEditorDialog(
            self.contact_db, 
            self.settings_manager, 
            self.data_validator,
            self.dialog_parent
        )
        dialog.exec_()

    def _on_query(self):
        """Handle Query menu action."""
        logger.info("Query action triggered")
        from app.ui.query_dialog import QueryDialog
        dialog = QueryDialog(self.contact_db, self.dialog_parent)
        dialog.exec_()

    def _on_today(self):
        """Handle Today's Namedays menu action."""
        logger.info("Today's namedays action triggered")
        from app.ui.today_namedays_dialog import TodayNamedaysDialog
        dialog = TodayNamedaysDialog(self.contact_db, self.nameday_ref, self.dialog_parent)
        dialog.exec_()

    def _on_exit(self):
        """Handle Exit menu action."""
        logger.info("Exit action triggered")
        QApplication.instance().quit()

    def _on_reload_namedays(self):
        """Handle Reload Namedays Database menu action [REQ-0066]."""
        logger.info("Reload Namedays Database action triggered [REQ-0066]")
        
        try:
            # Reload the namedays database
            success, message = self.nameday_ref.reload()
            
            if success:
                # Show success notification
                self.show_message(
                    self.tr("Database Reloaded"),
                    message,
                    duration=3000
                )
                logger.info(f"✓ Namedays database reloaded: {message} [REQ-0066]")
            else:
                # Show error notification
                self.show_message(
                    self.tr("Reload Failed"),
                    message,
                    duration=5000
                )
                logger.error(f"✗ Failed to reload namedays: {message} [REQ-0066]")
                
        except Exception as e:
            logger.error(f"✗ Unexpected error during reload: {e} [REQ-0066]")
            self.show_message(
                self.tr("Reload Failed"),
                self.tr("Unexpected error: ") + str(e),
                duration=5000
            )
