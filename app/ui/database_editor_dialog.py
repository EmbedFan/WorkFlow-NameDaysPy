from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem, 
    QPushButton, QHeaderView, QWidget, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from pathlib import Path

from app.utils import get_logger
from app.constants import RESOURCES_DIR
from app.ui.add_edit_contact_dialog import AddEditContactDialog
from app.exceptions import DatabaseException

logger = get_logger(__name__)


class DatabaseEditorDialog(QDialog):
    """Contact database editor dialog [REQ-0011, REQ-0049]."""
    
    def __init__(self, contact_db, settings_manager, data_validator=None, parent=None):
        super().__init__(parent)
        self.contact_db = contact_db
        self.settings_manager = settings_manager  # For column width persistence [REQ-0056-0060]
        self.data_validator = data_validator  # For contact validation in add/edit dialog [REQ-0040]
        
        # Load dialog configuration (size and column widths) [REQ-0061]
        self.dialog_config = self._load_dialog_config()
        
        self.setWindowTitle(self.tr("Contact Database"))
        
        # Load and set database icon [REQ-0011]
        icon_path = RESOURCES_DIR / "database.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        width, height = self.dialog_config["window_size"]
        self.setGeometry(100, 100, width, height)
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup UI components [REQ-0011, REQ-0049]."""
        layout = QVBoxLayout()
        
        # Table for contacts
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            self.tr("Name"),                # 0 - Resizable, Saved
            self.tr("Main Nameday"),        # 1 - Auto-fitted only (not saved)
            self.tr("Other Nameday"),       # 2 - Resizable, Saved
            self.tr("Recipient"),           # 3 - Resizable, Saved
            self.tr("Email"),               # 4 - Resizable, Saved
            self.tr("Comment"),             # 5 - Resizable, Saved (user control)
            self.tr("Disabled"),            # 6 - Auto-fitted only (not saved)
            self.tr("Actions")              # 7 - Auto-fitted only (not saved)
        ])
        
        # Enable manual column resizing [REQ-0056]
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        
        # Populate table with action buttons
        self._refresh_table()
        
        layout.addWidget(self.table)
        
        # Apply column widths: config first, then auto-fit fallback [REQ-0060, REQ-0061, REQ-0062]
        # If column widths are in config, apply them and skip auto-fit [REQ-0062]
        # Otherwise, auto-fit columns [REQ-0057]
        if self.dialog_config["column_widths"]:
            self._apply_loaded_column_widths(self.dialog_config["column_widths"])
        else:
            self._auto_fit_columns()  # Fallback when config missing [REQ-0057]
        
        # Buttons
        button_layout = QHBoxLayout()
        add_btn = QPushButton(self.tr("Add Contact"))
        add_btn.clicked.connect(self._on_add)
        
        close_btn = QPushButton(self.tr("Close"))
        close_btn.clicked.connect(self._on_close)
        
        button_layout.addWidget(add_btn)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    # ===== Dialog Configuration Management [REQ-0061, REQ-0062] =====
    
    def _load_dialog_config(self):
        """Load dialog configuration from settings [REQ-0061, REQ-0062].
        
        Loads: window size and column widths from config.json
        Returns: dict with 'window_size' (tuple) and 'column_widths' (dict)
        Fallbacks: (900, 600) for window size, empty dict for column widths (triggers auto-fit)
        """
        try:
            # Load window size [REQ-0061]
            window_size = self.settings_manager.get_dialog_window_size()
            
            # Load column widths [REQ-0060]
            column_widths = self.settings_manager.get_all_column_widths()
            
            logger.info(f"Loaded dialog config: window={window_size}, columns={len(column_widths)} [REQ-0061]")
            
            return {
                "window_size": window_size,
                "column_widths": column_widths if column_widths else {}
            }
        except Exception as e:
            logger.error(f"Failed to load dialog config, using defaults: {e}")
            return {
                "window_size": (900, 600),
                "column_widths": {}
            }
    
    def _apply_loaded_column_widths(self, widths):
        """Apply column widths from config, skipping auto-fit [REQ-0062].
        
        Args:
            widths: Dictionary of column_name -> width_px from config
        """
        try:
            column_mapping = {
                0: "Name",
                1: "Main Nameday",
                2: "Other Nameday",
                3: "Recipient",
                4: "Email",
                5: "Comment",
                6: "Disabled",
                7: "Actions"
            }
            
            applied_count = 0
            for col_index, col_name in column_mapping.items():
                if col_name in widths and widths[col_name] > 0:
                    self.table.setColumnWidth(col_index, widths[col_name])
                    applied_count += 1
            
            if applied_count > 0:
                logger.info(f"Applied {applied_count} column widths from config, skipping auto-fit [REQ-0062]")
            else:
                logger.debug("No column widths applied from config, using auto-fit [REQ-0062]")
                self._auto_fit_columns()
        except Exception as e:
            logger.warning(f"Failed to apply loaded column widths: {e}, using auto-fit fallback")
            self._auto_fit_columns()
    
    # ===== Column Width Management Methods [REQ-0056-0060] =====
    
    def _auto_fit_columns(self):
        """Auto-fit columns to content or header text [REQ-0057].
        
        Auto-fits: Name, Main Nameday, Other Nameday, Recipient, Email, Disabled, Actions
        NOT auto-fitted: Comment (user controls via manual resize)
        """
        # Column mapping: index → column name
        auto_fit_columns = {
            0: "Name",
            1: "Main Nameday", 
            2: "Other Nameday",
            3: "Recipient",
            4: "Email",
            6: "Disabled",
            7: "Actions"
        }
        
        for col_index, col_name in auto_fit_columns.items():
            # Calculate max width of header and content
            header_width = self.table.horizontalHeader().fontMetrics().width(col_name)
            content_widths = []
            
            for row in range(self.table.rowCount()):
                item = self.table.item(row, col_index)
                if item:
                    item_width = self.table.fontMetrics().width(item.text()) + 10
                    content_widths.append(item_width)
            
            # Set column width to max of header or content
            max_width = max([header_width] + content_widths) if content_widths else header_width
            self.table.setColumnWidth(col_index, max_width + 20)  # Add padding
            logger.info(f"Auto-fitted {col_name} (col {col_index}) to {max_width + 20}px [REQ-0057]")
    
    def _load_column_widths_from_config(self):
        """Load column widths from configuration [REQ-0060].
        
        Returns:
            True if widths loaded from config, False if using defaults
        """
        try:
            widths = self.settings_manager.get_all_column_widths()
            
            column_mapping = {
                0: "Name",
                1: "Main Nameday",
                2: "Other Nameday",
                3: "Recipient",
                4: "Email",
                5: "Comment",
                6: "Disabled",
                7: "Actions"
            }
            
            if not widths:
                logger.debug("No saved column widths found [REQ-0060]")
                return False
            
            loaded_count = 0
            for col_index, col_name in column_mapping.items():
                if col_name in widths and widths[col_name] > 0:
                    self.table.setColumnWidth(col_index, widths[col_name])
                    logger.info(f"Loaded saved width for {col_name}: {widths[col_name]}px [REQ-0060]")
                    loaded_count += 1
            
            if loaded_count == 0:
                logger.debug("No widths applied from config [REQ-0060]")
                return False
            
            return True
        except Exception as e:
            logger.warning(f"Failed to load column widths, using defaults: {e}")
            return False
    
    def closeEvent(self, event):
        """Save dialog configuration when dialog closes via system X button [REQ-0059, REQ-0061].
        
        Calls shared _save_dialog_config() helper so both Close button and system X button
        save the dialog configuration.
        """
        self._save_dialog_config()
        super().closeEvent(event)
    
    # ===== Close Handler & Config Save =====
    
    def _save_dialog_config(self) -> None:
        """Save dialog window size and column widths to config [REQ-0059, REQ-0061].
        
        Extracted as helper method so it can be called from both:
        - _on_close() button handler
        - closeEvent() system window close
        """
        try:
            # Save dialog window size [REQ-0061]
            width = self.geometry().width()
            height = self.geometry().height()
            self.settings_manager.save_dialog_window_size(width, height)
            logger.info(f"Saved dialog window size: {width}x{height} [REQ-0061]")
            
            # Save column widths [REQ-0059]
            widths_to_save = {}
            # Only save configurable columns per REQ-0059
            column_mapping = {
                0: "Name",
                2: "Other Nameday",
                3: "Recipient",
                4: "Email",
                5: "Comment"
            }
            
            for col_index, col_name in column_mapping.items():
                width = self.table.columnWidth(col_index)
                if width > 0:
                    widths_to_save[col_name] = width
            
            if widths_to_save:
                self.settings_manager.save_column_widths(widths_to_save)
                logger.info(f"Saved {len(widths_to_save)} column widths to config: {widths_to_save} [REQ-0059]")
            else:
                logger.warning("No column widths to save [REQ-0059]")
                
        except Exception as e:
            logger.error(f"Failed to save dialog configuration: {e}")
    
    def _on_close(self) -> None:
        """Handle Close button click - save config and close dialog [REQ-0059, REQ-0061].
        
        Ensures that clicking the "Close" button also saves dialog size and column widths,
        not just the system X button.
        """
        self._save_dialog_config()
        self.accept()
    
    # ===== Table Refresh & Rendering =====
    
    def _refresh_table(self) -> None:
        """Reload contact data from database and redraw table [REQ-0011].
        
        Called after add/edit/delete operations to ensure UI reflects
        current database state.
        """
        self.table.setRowCount(0)  # Clear
        
        contacts = self.contact_db.read_contacts()
        self.table.setRowCount(len(contacts))
        
        for row, contact in enumerate(contacts):
            self.table.setItem(row, 0, QTableWidgetItem(contact.name))
            self.table.setItem(row, 1, QTableWidgetItem(contact.main_nameday))
            self.table.setItem(row, 2, QTableWidgetItem(contact.other_nameday or ""))
            self.table.setItem(row, 3, QTableWidgetItem(contact.recipient))
            self.table.setItem(row, 4, QTableWidgetItem(", ".join(contact.email_addresses)))
            self.table.setItem(row, 5, QTableWidgetItem(contact.comment or ""))
            self.table.setItem(row, 6, QTableWidgetItem(str(contact.notification_disabled)))
            
            # Add edit/delete buttons in column 7 (Actions)
            action_widget = self._create_action_buttons(row)
            self.table.setCellWidget(row, 7, action_widget)
        
        logger.info(f"Table refreshed: {len(contacts)} contacts loaded")
    
    def _create_action_buttons(self, row: int) -> QWidget:
        """Create edit/delete action buttons for table row.
        
        Args:
            row: Row index for this action button pair
        
        Returns:
            QWidget containing Edit and Delete buttons
        """
        widget = QWidget()
        layout = QHBoxLayout(widget)
        
        edit_btn = QPushButton(self.tr("Edit"))
        edit_btn.clicked.connect(lambda: self._on_edit_row(row))
        layout.addWidget(edit_btn)
        
        delete_btn = QPushButton(self.tr("Delete"))
        delete_btn.clicked.connect(lambda: self._on_delete_row(row))
        layout.addWidget(delete_btn)
        
        layout.setContentsMargins(0, 0, 0, 0)
        return widget
    
    # ===== Event Handlers: Add/Edit/Delete =====
    
    def _on_add(self):
        """Open add contact dialog for creating new contact [REQ-0011, REQ-0017]."""
        logger.info("Add contact action")
        
        dialog = AddEditContactDialog(
            contact_db_manager=self.contact_db,
            data_validator=self.data_validator,
            contact=None,  # ADD mode
            parent=self
        )
        
        if dialog.exec_() == QDialog.Accepted:
            logger.info("New contact added successfully")
            self._refresh_table()
    
    def _on_edit_row(self, row: int):
        """Open edit contact dialog for modifying selected contact.
        
        Args:
            row: Row index to edit
        """
        contacts = self.contact_db.read_contacts()
        
        if row >= len(contacts):
            logger.error(f"Invalid row index: {row}")
            return
        
        selected_contact = contacts[row]
        logger.info(f"Edit contact action: {selected_contact.name}")
        
        dialog = AddEditContactDialog(
            contact_db_manager=self.contact_db,
            data_validator=self.data_validator,
            contact=selected_contact,  # EDIT mode
            parent=self
        )
        
        if dialog.exec_() == QDialog.Accepted:
            logger.info(f"Contact updated: {selected_contact.name}")
            self._refresh_table()
    
    def _on_delete_row(self, row: int):
        """Delete contact at specific row with confirmation.
        
        Args:
            row: Row index to delete
        """
        contacts = self.contact_db.read_contacts()
        
        if row >= len(contacts):
            logger.error(f"Invalid row index for deletion: {row}")
            return
        
        contact = contacts[row]
        
        reply = QMessageBox.question(
            self,
            self.tr("Confirm Delete"),
            self.tr(f"Delete contact '{contact.name}'?"),
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                self.contact_db.delete_contact(contact.name)
                logger.info(f"Contact deleted: {contact.name}")
                self._refresh_table()
            except DatabaseException as e:
                QMessageBox.critical(
                    self,
                    self.tr("Delete Failed"),
                    self.tr(f"Error deleting contact: {str(e)}")
                )