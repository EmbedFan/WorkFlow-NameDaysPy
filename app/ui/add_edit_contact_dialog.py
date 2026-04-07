"""
Contact record add/edit dialog for CRUD operations [REQ-0011, REQ-0017, REQ-0049].

Modal dialog supporting both ADD (create new) and EDIT (modify existing) modes
with integrated three-layer validation (UI, business logic, persistence).
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QCheckBox, QPlainTextEdit, QListWidget,
    QListWidgetItem, QMessageBox, QInputDialog
)
from PyQt5.QtCore import Qt

from app.types import Contact
from app.utils import get_logger
from app.exceptions import ValidationException, DatabaseException

logger = get_logger(__name__)


class AddEditContactDialog(QDialog):
    """
    Contact record add/edit dialog [REQ-0011, REQ-0017, REQ-0049].
    
    Manages creation of new contacts (add mode) or modification of existing contacts
    (edit mode). Integrates form validation (3 layers), error display, and CRUD operations.
    """
    
    def __init__(self, contact_db_manager, data_validator,
                 contact=None, parent=None):
        """
        Initialize dialog in ADD or EDIT mode.
        
        Args:
            contact_db_manager (ContactDatabaseManager): For CRUD operations
            data_validator (DataValidator): For business logic validation
            contact (Contact, optional): Contact to edit. None for add mode.
            parent (QWidget, optional): Parent widget
        """
        super().__init__(parent)
        
        self.contact_db = contact_db_manager
        self.validator = data_validator
        self.contact = contact  # None → ADD mode, Contact → EDIT mode
        self.is_edit_mode = contact is not None
        
        # Window setup
        self.setWindowTitle(
            self.tr("Edit Contact") if self.is_edit_mode
            else self.tr("Add New Contact")
        )
        self.setGeometry(100, 100, 600, 700)
        self.setModal(True)
        
        # UI initialization
        self._setup_ui()
        self._load_contact_data()
    
    def _setup_ui(self):
        """Setup form fields and layout."""
        main_layout = QVBoxLayout()
        
        # Required fields section
        name_label = QLabel(self.tr("Contact Name *"))
        main_layout.addWidget(name_label)
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(self.tr("Enter contact name"))
        main_layout.addWidget(self.name_input)
        
        main_nameday_label = QLabel(self.tr("Main Nameday (MM-DD) *"))
        main_layout.addWidget(main_nameday_label)
        
        self.main_nameday_input = QLineEdit()
        self.main_nameday_input.setInputMask("99-99")
        self.main_nameday_input.setPlaceholderText(self.tr("MM-DD (e.g., 12-25)"))
        main_layout.addWidget(self.main_nameday_input)
        
        recipient_label = QLabel(self.tr("Recipient *"))
        main_layout.addWidget(recipient_label)
        
        self.recipient_input = QLineEdit()
        self.recipient_input.setPlaceholderText(self.tr("Recipient name/label"))
        main_layout.addWidget(self.recipient_input)
        
        # Optional fields section
        other_nameday_label = QLabel(self.tr("Other Nameday (MM-DD)"))
        main_layout.addWidget(other_nameday_label)
        
        self.other_nameday_input = QLineEdit()
        self.other_nameday_input.setInputMask("99-99")
        self.other_nameday_input.setPlaceholderText(self.tr("MM-DD (optional)"))
        main_layout.addWidget(self.other_nameday_input)
        
        # Email list section
        email_label = QLabel(self.tr("Email Addresses"))
        main_layout.addWidget(email_label)
        
        self.email_list = QListWidget()
        main_layout.addWidget(self.email_list)
        
        email_button_layout = QHBoxLayout()
        add_email_btn = QPushButton(self.tr("Add Email"))
        add_email_btn.clicked.connect(self._on_add_email)
        remove_email_btn = QPushButton(self.tr("Remove Selected"))
        remove_email_btn.clicked.connect(self._on_remove_email)
        email_button_layout.addWidget(add_email_btn)
        email_button_layout.addWidget(remove_email_btn)
        email_button_layout.addStretch()
        main_layout.addLayout(email_button_layout)
        
        # Prewritten email
        prewritten_label = QLabel(self.tr("Prewritten Email"))
        main_layout.addWidget(prewritten_label)
        
        self.prewritten_email_input = QPlainTextEdit()
        self.prewritten_email_input.setPlaceholderText(
            self.tr("Optional email template")
        )
        self.prewritten_email_input.setMaximumHeight(60)
        main_layout.addWidget(self.prewritten_email_input)
        
        # Comment
        comment_label = QLabel(self.tr("Comment"))
        main_layout.addWidget(comment_label)
        
        self.comment_input = QPlainTextEdit()
        self.comment_input.setPlaceholderText(self.tr("Optional notes"))
        self.comment_input.setMaximumHeight(60)
        main_layout.addWidget(self.comment_input)
        
        # Notification checkbox
        self.notification_disabled_checkbox = QCheckBox(
            self.tr("Disable Notifications")
        )
        main_layout.addWidget(self.notification_disabled_checkbox)
        
        main_layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        save_btn = QPushButton(self.tr("Save"))
        save_btn.clicked.connect(self._on_save)
        cancel_btn = QPushButton(self.tr("Cancel"))
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(save_btn)
        button_layout.addWidget(cancel_btn)
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def _load_contact_data(self):
        """Load contact data into form (EDIT mode only)."""
        if not self.is_edit_mode:
            return
        
        self.name_input.setText(self.contact.name)
        self.main_nameday_input.setText(self.contact.main_nameday)
        self.recipient_input.setText(self.contact.recipient)
        
        if self.contact.other_nameday:
            self.other_nameday_input.setText(self.contact.other_nameday)
        
        for email in self.contact.email_addresses:
            self.email_list.addItem(email)
        
        if self.contact.prewritten_email:
            self.prewritten_email_input.setPlainText(self.contact.prewritten_email)
        
        if self.contact.comment:
            self.comment_input.setPlainText(self.contact.comment)
        
        self.notification_disabled_checkbox.setChecked(
            self.contact.notification_disabled
        )
        
        logger.info(f"Loaded contact data for editing: {self.contact.name}")
    
    def _validate_fields(self) -> list:
        """
        Layer 1: UI field validation.
        
        Checks required fields at UI level before deeper validation.
        
        Returns:
            List of error messages (empty if valid)
        """
        errors = []
        
        if not self.name_input.text().strip():
            errors.append(self.tr("Name is required"))
        
        if not self.main_nameday_input.text().strip():
            errors.append(self.tr("Main nameday is required"))
        
        if not self.recipient_input.text().strip():
            errors.append(self.tr("Recipient is required"))
        
        return errors
    
    def _build_contact_from_form(self) -> Contact:
        """Build Contact object from form fields."""
        # Properly handle email list
        email_list = [
            self.email_list.item(i).text()
            for i in range(self.email_list.count())
        ]
        
        # Handle masked input fields: "99-99" input mask returns " - " when empty
        # Convert to None if empty or contains only spaces/dashes
        other_nameday_text = self.other_nameday_input.text().strip()
        other_nameday = (
            other_nameday_text 
            if other_nameday_text and other_nameday_text != "-" 
            else None
        )
        
        return Contact(
            name=self.name_input.text().strip(),
            main_nameday=self.main_nameday_input.text().strip(),
            recipient=self.recipient_input.text().strip(),
            other_nameday=other_nameday,
            email_addresses=email_list,
            prewritten_email=self.prewritten_email_input.toPlainText().strip() or None,
            comment=self.comment_input.toPlainText().strip() or None,
            notification_disabled=self.notification_disabled_checkbox.isChecked()
        )
    
    def _display_errors(self, errors: list, title: str = "Error"):
        """Display error messages to user in prominent message box."""
        message = "\n".join([f"• {e}" for e in errors])
        QMessageBox.warning(
            self,
            title,
            self.tr(f"Please correct the following:\n\n{message}"),
            QMessageBox.Ok
        )
    
    def _validate_and_save(self) -> bool:
        """
        Three-layer validation and persistence orchestration [REQ-0040, REQ-0049].
        
        Process:
            1. Layer 1: UI field validation
               → If fail: Display errors, return False
            
            2. Build Contact object from form fields
            
            3. Layer 2: Business logic validation via DataValidator
               → If fail: Display errors, return False
            
            4. Layer 3: CRUD persistence
               → If fail: Display error, return False
            
            5. Success: Close dialog (accept), return True
        
        Returns:
            True if successfully validated and persisted
        """
        
        # Layer 1: UI Validation
        ui_errors = self._validate_fields()
        if ui_errors:
            self._display_errors(ui_errors, title=self.tr("Form Validation"))
            return False
        
        logger.info("Layer 1 (UI validation): Passed")
        
        # Build Contact object from form
        contact = self._build_contact_from_form()
        
        # Layer 2: Business Logic Validation
        validation_errors = self.validator.validate_contact(contact)
        if validation_errors:
            self._display_errors(validation_errors, title=self.tr("Data Validation"))
            return False
        
        logger.info("Layer 2 (business logic validation): Passed")
        
        # Layer 3: Persistence
        if not self._persist_contact(contact):
            self._display_errors(
                [self.tr("Failed to save contact to database")],
                title=self.tr("Persistence Error")
            )
            return False
        
        logger.info("Layer 3 (persistence): Passed")
        
        # Invalidate monitoring cache so newly added contacts are detected [REQ-0065]
        # This ensures next monitoring cycle performs fresh check of updated database
        try:
            from app.main import NameDaysMonitoringApp
            app = NameDaysMonitoringApp.instance()
            if app and hasattr(app, 'monitoring_engine'):
                app.monitoring_engine.invalidate_check_cache()
                logger.info("Monitoring cache invalidated after contact save [REQ-0065]")
        except Exception as e:
            logger.warning(f"Failed to invalidate monitoring cache: {e}")
        
        # Success
        self.accept()
        return True
    
    def _persist_contact(self, contact: Contact) -> bool:
        """
        Attempt to persist contact to database [REQ-0017, REQ-0037].
        
        Operation:
            - ADD mode: self.contact_db.create_contact(contact)
            - EDIT mode: self.contact_db.update_contact(original_name, contact)
        
        Returns:
            True if successfully persisted, False if error
        """
        try:
            if self.is_edit_mode:
                original_name = self.contact.name
                self.contact_db.update_contact(original_name, contact)
                logger.info(f"Contact updated: {contact.name}")
            else:
                self.contact_db.create_contact(contact)
                logger.info(f"Contact created: {contact.name}")
            
            return True
        except (ValidationException, DatabaseException) as e:
            logger.error(f"Failed to persist contact: {e}")
            return False
    
    def _on_save(self):
        """Save button click handler."""
        self._validate_and_save()
    
    def _on_add_email(self):
        """Add email address to list."""
        email, ok = QInputDialog.getText(
            self,
            self.tr("Add Email Address"),
            self.tr("Enter email address:")
        )
        
        if ok and email:
            if self.validator.validate_email(email):
                self.email_list.addItem(email)
                logger.info(f"Email added to list: {email}")
            else:
                QMessageBox.warning(
                    self,
                    self.tr("Invalid Email"),
                    self.tr(f"'{email}' is not a valid email address")
                )
    
    def _on_remove_email(self):
        """Remove selected email from list."""
        current = self.email_list.currentRow()
        if current >= 0:
            email = self.email_list.item(current).text()
            self.email_list.takeItem(current)
            logger.info(f"Email removed from list: {email}")
