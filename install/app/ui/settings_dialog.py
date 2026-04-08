from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSpinBox, QCheckBox, QPushButton, QComboBox, QMessageBox
)
from PyQt5.QtCore import Qt
import sys

from app.utils import get_logger
from app.constants import SUPPORTED_LANGUAGES
from app.services.windows_startup import WindowsStartupManager
from app.exceptions import WindowsIntegrationException

logger = get_logger(__name__)


class SettingsDialog(QDialog):
    """Settings configuration dialog."""
    
    def __init__(self, settings_manager, parent=None):
        super().__init__(parent)
        self.settings_manager = settings_manager
        self.settings = settings_manager.get_settings()
        
        self.setWindowTitle(self.tr("Settings"))
        self.setGeometry(100, 100, 400, 300)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI components."""
        layout = QVBoxLayout()
        
        # Check interval
        interval_layout = QHBoxLayout()
        interval_layout.addWidget(QLabel(self.tr("Check Interval (minutes):")))
        self.interval_spin = QSpinBox()
        self.interval_spin.setMinimum(1)
        self.interval_spin.setMaximum(1440)
        self.interval_spin.setValue(self.settings.check_interval)
        interval_layout.addWidget(self.interval_spin)
        layout.addLayout(interval_layout)
        
        # Auto-launch
        self.auto_launch_check = QCheckBox(self.tr("Start at Windows startup"))
        self.auto_launch_check.setChecked(self.settings.auto_launch)
        layout.addWidget(self.auto_launch_check)
        
        # Notifications enabled
        self.notifications_check = QCheckBox(self.tr("Enable notifications")) 
        self.notifications_check.setChecked(self.settings.notifications_enabled)
        layout.addWidget(self.notifications_check)
        
        # Language selection [REQ-0045]
        language_layout = QHBoxLayout()
        language_layout.addWidget(QLabel(self.tr("Language:")))
        self.language_combo = QComboBox()
        
        # Add supported languages
        language_names = {
            "en": "English",
            "hu": "Magyar (Hungarian)"
        }
        for lang_code in SUPPORTED_LANGUAGES:
            self.language_combo.addItem(language_names.get(lang_code, lang_code), lang_code)
        
        # Set current language
        current_idx = self.language_combo.findData(self.settings_manager.language)
        if current_idx >= 0:
            self.language_combo.setCurrentIndex(current_idx)
        
        language_layout.addWidget(self.language_combo)
        layout.addLayout(language_layout)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton(self.tr("Save"))
        save_btn.clicked.connect(self._on_save)
        cancel_btn = QPushButton(self.tr("Cancel"))
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _on_save(self):
        """Save settings."""
        # Track auto-launch change [REQ-0002, REQ-0051]
        old_auto_launch = self.settings.auto_launch
        new_auto_launch = self.auto_launch_check.isChecked()
        auto_launch_changed = (old_auto_launch != new_auto_launch)
        
        # Get new language selection
        new_language = self.language_combo.currentData()
        old_language = self.settings_manager.language
        language_changed = (new_language != old_language)
        
        # Save all settings
        logger.info("Settings saving...")
        self.settings_manager.set_setting("check_interval", self.interval_spin.value())
        self.settings_manager.set_setting("auto_launch", new_auto_launch)
        self.settings_manager.set_setting("notifications_enabled", self.notifications_check.isChecked())
        self.settings_manager.set_setting("language", new_language)
        
        # Handle auto-launch registry update [REQ-0002, REQ-0051]
        if auto_launch_changed:
            try:
                manager = WindowsStartupManager()
                
                if new_auto_launch:
                    # Get Python executable path
                    app_path = f'{sys.executable} "{sys.argv[0]}"'
                    manager.enable_auto_launch(app_path)
                    logger.info(f"Auto-launch enabled: {app_path} [REQ-0002]")
                    QMessageBox.information(
                        self,
                        self.tr("Auto-launch Enabled"),
                        self.tr("Application will start at Windows startup on next restart.")
                    )
                else:
                    manager.disable_auto_launch()
                    logger.info("Auto-launch disabled [REQ-0002]")
                    QMessageBox.information(
                        self,
                        self.tr("Auto-launch Disabled"),
                        self.tr("Application will no longer start at Windows startup.")
                    )
            except WindowsIntegrationException as e:
                logger.error(f"Failed to update auto-launch registry: {e}")
                QMessageBox.warning(
                    self,
                    self.tr("Failed to Update Startup"),
                    self.tr(f"Could not update Windows startup registry: {str(e)}")
                )
                # Still save config even if registry update fails
        
        # If language changed, notify user and switch translator [REQ-0045]
        if language_changed:
            from app.i18n.translator import switch_language
            from PyQt5.QtWidgets import QApplication
            
            switch_language(QApplication.instance(), new_language)
            
            QMessageBox.information(
                self,
                self.tr("Language Changed"),
                self.tr("Language will be fully applied after application restart.")
            )
            logger.info(f"Language switched from {old_language} to {new_language} [REQ-0045]")
        
        logger.info("Settings saved successfully")
        self.accept()