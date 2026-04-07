# Contact Record Add/Edit Implementation Plan
**Document:** `impl_contact_db_edit_additionals.md`  
**Related Requirements:** REQ-0011, REQ-0017, REQ-0029–REQ-0036, REQ-0040, REQ-0045–REQ-0046, REQ-0049  
**Status:** Architecture & Implementation Specification  
**Last Updated:** 2026-04-01

---

## 1. Executive Summary

This document provides comprehensive architectural guidance for implementing the **Add/Edit Contact Record** functionality. The feature enables users to create new contacts and modify existing contacts through a modal dialog interface, with integrated validation, error handling, and CRUD operation management.

**Key Deliverables:**
- New dialog class: `AddEditContactDialog` (modal QDialog)
- Three-layer validation strategy (UI-level, business logic, persistence)
- Seamless integration with `DatabaseEditorDialog`
- Full i18n support for multi-language deployment
- Comprehensive error feedback to users

**Architecture Approach:** Separate modal dialog (not inline editing) following established PyQt5 patterns in the codebase, supporting 7 contact fields with contextual validation and visual feedback.

---

## 2. Requirements Mapping

| Requirement ID | Description | Implementation Aspect |
|---|---|---|
| **REQ-0011** | Contact database editor with add/remove/modify operations | Dialog class with CRUD method wiring |
| **REQ-0017** | CRUD operations with CSV persistence and data validation | Contact creation/update via ContactDatabaseManager |
| **REQ-0029** | Contact record data structure (7 fields) | Form fields in AddEditContactDialog |
| **REQ-0030** | Contact name field (required) | QLineEdit with non-empty validation |
| **REQ-0031** | Main nameday field in MM-DD format (required) | Date input control with format validation |
| **REQ-0032** | Other nameday field (optional, MM-DD format) | Optional date input control |
| **REQ-0033** | Recipient field (required) | QLineEdit with non-empty validation |
| **REQ-0034** | Email addresses list (optional) | QListWidget with add/remove buttons |
| **REQ-0035** | Prewritten email template (optional) | QPlainTextEdit |
| **REQ-0036** | Comment field (optional) | QPlainTextEdit |
| **REQ-0040** | Data validation before storage | Three-layer validation (UI, business logic, CSV) |
| **REQ-0045** | Multi-language UI support | Translation keys (i18n) for all strings |
| **REQ-0046** | Language-specific date/time formatting | MM-DD format consistent across locales |
| **REQ-0049** | Database editor interface with validation feedback | Error display in modal dialog |

---

## 3. Architecture Overview

### 3.1 Design Pattern: Modal Dialog + Manager Integration

```
DatabaseEditorDialog
    ├── _on_add() → AddEditContactDialog(contact=None, mode=ADD)
    ├── _on_edit() → AddEditContactDialog(contact=existing, mode=EDIT)
    └── _refresh_table() ← Dialog.accept()

AddEditContactDialog
    ├── Form fields (7 contact attributes)
    ├── Validation (3 layers)
    ├── CRUD operations via ContactDatabaseManager
    └── Error feedback (visual & message boxes)
```

### 3.2 Modal Dialog Rationale

**Why separate modal dialog (not inline editing)?**

| Aspect | Inline Editing | Modal Dialog | Our Choice |
|--------|----------------|--------------|-----------|
| Complex form (7 fields, different types) | ❌ Poor | ✅ Excellent | Modal |
| MM-DD date validation/picker | ❌ Difficult | ✅ Dedicated | Modal |
| Email list management (add/remove) | ❌ Complex | ✅ Clear UI | Modal |
| Error display prominence | ❌ Inline hints | ✅ Message box | Modal |
| Multi-layer validation flow | ❌ Unclear state | ✅ Clear steps | Modal |
| Consistency with existing dialogs | ❌ New pattern | ✅ Matches codebase | Modal |

**Conclusion:** Modal dialog best supports validation complexity and user feedback requirements (REQ-0040, REQ-0049).

---

## 4. Detailed Design Specification

### 4.1 Class Structure: AddEditContactDialog

```python
class AddEditContactDialog(QDialog):
    """
    Contact record add/edit dialog [REQ-0011, REQ-0017, REQ-0049].
    
    Manages creation of new contacts (add mode) or modification of existing contacts
    (edit mode). Integrates form validation (3 layers), error display, and CRUD operations.
    
    Design Pattern:
        - Modal dialog inheriting from QDialog
        - Takes ContactDatabaseManager + DataValidator as dependencies (DI)
        - In ADD mode: contact parameter is None
        - In EDIT mode: contact parameter is existing Contact object
        - Dual-mode form that loads data if editing, starts blank if adding
    
    Requirements Addressed:
        - REQ-0011: Database editor with add/modify operations
        - REQ-0017: CRUD operations (create/update)
        - REQ-0029-0036: All 7 contact fields
        - REQ-0040: Data validation before storage
        - REQ-0049: Validation feedback display
        - REQ-0045-0046: i18n support with MM-DD date format
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
        self.contact = contact  # None if ADD mode, Contact if EDIT mode
        self.is_edit_mode = contact is not None
        
        # Setup window
        self.setWindowTitle(
            self.tr("Edit Contact") if self.is_edit_mode 
            else self.tr("Add New Contact")
        )
        self.setGeometry(100, 100, 600, 700)
        self.setModal(True)
        
        self._setup_ui()
        self._load_contact_data()  # Populate fields if editing
```

### 4.2 UI Components: Field Definitions

**Group 1: Required Fields**

| Field | Type | Validation | Qt Component | Notes |
|-------|------|-----------|--------------|-------|
| `name` | String | Non-empty, < 100 chars | QLineEdit | Contact name (REQ-0030) |
| `main_nameday` | MM-DD | Valid month (01-12), day (01-31) | Custom MM-DD input | REQ-0031, REQ-0023 |
| `recipient` | String | Non-empty, < 100 chars | QLineEdit | Recipients (REQ-0033) |

**Group 2: Optional Fields**

| Field | Type | Validation | Qt Component | Notes |
|-------|------|-----------|--------------|-------|
| `other_nameday` | MM-DD | Valid MM-DD or empty | Custom MM-DD input | Secondary nameday (REQ-0032) |
| `email_addresses` | List[str] | Valid email or empty | QListWidget + buttons | Multi-email support (REQ-0034) |
| `prewritten_email` | Text | None | QPlainTextEdit | Email template (REQ-0035) |
| `comment` | Text | None | QPlainTextEdit | Free-text note (REQ-0036) |

**Group 3: System Fields**

| Field | Type | Validation | Qt Component | Notes |
|-------|------|-----------|--------------|-------|
| `notification_disabled` | Boolean | None | QCheckBox | "Disable notifications" (REQ-0008) |

### 4.3 Date Field Handling: MM-DD Format

**Recommended Approach: Input Mask QLineEdit**

```python
def _create_nameday_field(self, field_name: str) -> QLineEdit:
    """Create MM-DD date input field with validation mask.
    
    Args:
        field_name: "Main Nameday" or "Other Nameday"
    
    Returns:
        Configured QLineEdit with MM-DD input mask
    
    Date Format:
        - MM: Month (01-12)
        - DD: Day (01-31)
        - Format: MM-DD (e.g., "12-25" for December 25th)
    """
    field = QLineEdit()
    field.setInputMask("99-99")  # Forces MM-DD pattern, prevents non-numeric input
    field.setPlaceholderText(self.tr("MM-DD (e.g., 12-25)"))
    field.setToolTip(self.tr("Enter nameday as MM-DD format"))
    field.setMaxLength(5)
    
    return field
```

**Pros:**
- ✅ Enforces MM-DD format at input time
- ✅ Prevents most invalid input (non-numeric)
- ✅ Simple, lightweight
- ✅ Consistent with REQ-0023 (MM-DD format requirement)

**Cons:**
- ⚠️ Doesn't validate month range (01-12) or day range (01-31) at input time
- ⚠️ Allows invalid dates like "99-99" or "13-32"
- → Solution: Validation happens in Layer 2 (DataValidator.validate_nameday_date)

**Alternative Approaches:**

*Option B: SpinBox Pair (Month + Day Separate)*
```python
month_spin = QSpinBox()
month_spin.setMinimum(1)
month_spin.setMaximum(12)

day_spin = QSpinBox()
day_spin.setMinimum(1)
day_spin.setMaximum(31)

# Reconstruct: f"{month_spin.value():02d}-{day_spin.value():02d}"
```
- Pros: Explicit range validation, clearer UX
- Cons: Two widgets, more space, loses direct typing

*Option C: Calendar Popup QCalendarWidget*
- Pros: Visual month/year selection
- Cons: Overkill for MM-DD format, inconsistent with core requirement

**Recommendation:** **Option A (Input Mask)** — simplest, consistent with requirements, validation deferred to Layer 2.

### 4.4 Email Address Management

**Implementation: QListWidget with Add/Remove UI**

```python
def _setup_email_section(self):
    """Create email addresses list widget with add/remove buttons.
    
    Layout:
        Email Addresses:
        [QListWidget showing: user1@example.com, user2@example.com]
        [Add Email Button] [Remove Selected Button]
    
    Interactions:
        - Add Email: Opens sub-dialog to enter and validate email
        - Remove: Deletes selected item from list
        - Validation: Each email validated per DataValidator.validate_email()
    
    Data Binding:
        - On init (edit mode): Populate list from contact.email_addresses
        - On save: Extract list from widget → contact.email_addresses
    """
    
    layout = QVBoxLayout()
    
    label = QLabel(self.tr("Email Addresses (optional)"))
    layout.addWidget(label)
    
    self.email_list = QListWidget()
    layout.addWidget(self.email_list)
    
    button_layout = QHBoxLayout()
    
    add_email_btn = QPushButton(self.tr("Add Email"))
    add_email_btn.clicked.connect(self._on_add_email)
    button_layout.addWidget(add_email_btn)
    
    remove_email_btn = QPushButton(self.tr("Remove Selected"))
    remove_email_btn.clicked.connect(self._on_remove_email)
    button_layout.addWidget(remove_email_btn)
    
    button_layout.addStretch()
    layout.addLayout(button_layout)
    
    return layout

def _on_add_email(self):
    """Open dialog to add new email address."""
    email, ok = QInputDialog.getText(
        self,
        self.tr("Add Email Address"),
        self.tr("Enter email address:")
    )
    
    if ok and email:
        # Validate before adding to list
        if self.validator.validate_email(email):
            self.email_list.addItem(email)
        else:
            QMessageBox.warning(
                self,
                self.tr("Invalid Email"),
                self.tr(f"'{email}' is not a valid email address")
            )
```

---

## 5. Validation Strategy: Three-Layer Approach

### 5.1 Validation Architecture

```
┌─────────────────────────────────────┐
│  Layer 1: UI/Field-Level Validation │
│  ─────────────────────────────────  │
│  • Non-empty required fields         │
│  • Basic format checks (length)      │
│  • Real-time feedback                │
│  Action: Show errors, prevent Layer 2│
└─────────────────┬───────────────────┘
                  │ (Pass)
┌─────────────────▼───────────────────┐
│ Layer 2: Business Logic Validation   │
│ ─────────────────────────────────  │
│  • DataValidator.validate_contact()  │
│  • MM-DD date format validation      │
│  • Email format validation           │
│  • Domain-specific rules             │
│  Action: Show errors, prevent Layer 3│
└─────────────────┬───────────────────┘
                  │ (Pass)
┌─────────────────▼───────────────────┐
│  Layer 3: Persistence (CRUD)         │
│  ─────────────────────────────────  │
│  • create_contact() [ADD mode]       │
│  • update_contact() [EDIT mode]      │
│  • CSV write to disk [REQ-0037]      │
│  Action: Persist, close dialog       │
└─────────────────────────────────────┘
```

### 5.2 Layer 1: UI Validation

```python
def _validate_fields(self) -> List[str]:
    """Validate required fields at UI level [REQ-0040].
    
    Checks:
        - name: non-empty
        - main_nameday: non-empty
        - recipient: non-empty
    
    Returns:
        List of error messages (empty if valid)
    """
    errors = []
    
    # Required field checks
    if not self.name_input.text().strip():
        errors.append(self.tr("Name is required"))
    
    if not self.main_nameday_input.text().strip():
        errors.append(self.tr("Main nameday is required"))
    
    if not self.recipient_input.text().strip():
        errors.append(self.tr("Recipient is required"))
    
    return errors
```

### 5.3 Layer 2: Business Logic Validation

```python
def _validate_business_logic(self, contact: Contact) -> List[str]:
    """Validate contact against business rules [REQ-0040].
    
    Delegates to DataValidator.validate_contact() which checks:
        - MM-DD date format for main_nameday, other_nameday
        - Email format validation (RFC 5322)
        - Field length constraints
        - Type constraints
    
    Returns:
        List of validation error messages
    """
    return self.validator.validate_contact(contact)
```

### 5.4 Layer 3: CRUD Persistence

```python
def _persist_contact(self, contact: Contact) -> bool:
    """Attempt to persist contact to database [REQ-0017, REQ-0037].
    
    Operation:
        - ADD mode: self.contact_db.create_contact(contact)
        - EDIT mode: self.contact_db.update_contact(original_name, contact)
    
    Persistence:
        - CSV write to disk (UTF-8, semicolon delimiter) [REQ-0037]
        - Timestamps updated (created_at preserved on edit, updated_at set)
        - Exception handling for disk I/O failures
    
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
```

### 5.5 Orchestration: _validate_and_save()

```python
def _validate_and_save(self) -> bool:
    """Orchestrate three-layer validation and persistence [REQ-0040, REQ-0049].
    
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
    
    # Build Contact object from form
    contact = self._build_contact_from_form()
    
    # Layer 2: Business Logic Validation
    validation_errors = self._validate_business_logic(contact)
    if validation_errors:
        self._display_errors(validation_errors, title=self.tr("Data Validation"))
        return False
    
    # Layer 3: Persistence
    if not self._persist_contact(contact):
        self._display_errors(
            [self.tr("Failed to save contact to database")],
            title=self.tr("Persistence Error")
        )
        return False
    
    # Success
    self.accept()
    return True
```

---

## 6. Error Display & User Feedback

### 6.1 Error Dialog Design

```python
def _display_errors(self, error_messages: List[str], 
                    title: str = "Error") -> None:
    """Display validation errors in prominent message box [REQ-0049].
    
    Design:
        - Title: Contextual (e.g., "Form Validation", "Data Validation")
        - Icon: Warning (yellow triangle)
        - Text: Bulleted list of errors
        - Button: OK (dismiss)
    
    REQ-0049 Compliance:
        - Visual feedback: Color-coded (warning icon)
        - Clear messaging: Specific error descriptions
        - Blocking: Modal dialog prevents further action until dismissed
        - Actionable: Errors point to specific field issues
    """
    message = "\n".join([f"• {msg}" for msg in error_messages])
    
    QMessageBox.warning(
        self,
        title,
        self.tr(f"Please correct the following errors:\n\n{message}"),
        QMessageBox.Ok
    )
```

### 6.2 Success Feedback

```python
def _on_save_click(self):
    """Handle Save button click."""
    success = self._validate_and_save()
    
    if success:
        # Auto-close dialog (accept() called in _validate_and_save)
        # Parent receives QDialog.Accepted signal
        # No additional notification needed (dialog close is feedback)
        pass
```

---

## 7. Integration with DatabaseEditorDialog

### 7.1 Current State (Before Integration)

[Reference: `app/ui/database_editor_dialog.py` lines 193-194]

```python
def _on_add(self):
    """Add new contact."""
    logger.info("Add contact action")
    # TODO: Open add contact dialog

def _on_delete(self):
    """Delete selected contact."""
    logger.info("Delete contact action")
    # TODO: Implement delete logic
```

### 7.2 Integration Requirement: Dependency Injection

**Problem:** `AddEditContactDialog` requires `DataValidator` instance, but `DatabaseEditorDialog` doesn't currently have access to it.

**Solution:** Extend `DatabaseEditorDialog.__init__()` to accept `data_validator` parameter.

```python
class DatabaseEditorDialog(QDialog):
    """Contact database editor dialog [REQ-0011, REQ-0049]."""
    
    def __init__(self, contact_db, settings_manager, 
                 data_validator=None, parent=None):  # NEW
        super().__init__(parent)
        self.contact_db = contact_db
        self.settings_manager = settings_manager
        self.data_validator = data_validator  # NEW
        
        self.setWindowTitle("Contact Database")
        self.setGeometry(100, 100, 800, 500)
        self._setup_ui()
```

### 7.3 Implement _on_add() for ADD Mode

```python
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
        self._refresh_table()  # Reload data from database
```

### 7.4 Implement _on_edit() for EDIT Mode

```python
def _on_edit(self):
    """Open edit contact dialog for modifying selected contact [REQ-0011, REQ-0017]."""
    selected_indexes = self.table.selectedIndexes()
    
    if not selected_indexes:
        QMessageBox.information(
            self,
            self.tr("No Selection"),
            self.tr("Please select a contact to edit")
        )
        return
    
    row = selected_indexes[0].row()
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
```

### 7.5 Implement _refresh_table()

```python
def _refresh_table(self) -> None:
    """Reload contact data from database and redraw table [REQ-0011].
    
    Called after add/edit/delete operations to ensure UI reflects
    current database state.
    
    Process:
        1. Clear existing rows from table
        2. Read fresh contact list from contact_db
        3. Rebuild table with new data
        4. Restore column widths from config (if saved)
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
```

### 7.6 Add Edit Button to Table Actions

```python
def _create_action_buttons(self, row: int) -> QWidget:
    """Create edit/delete action buttons for table row.
    
    Returns: QWidget containing Edit and Delete buttons
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

def _on_edit_row(self, row: int):
    """Edit contact at specific row."""
    contacts = self.contact_db.read_contacts()
    if row < len(contacts):
        self.table.selectRow(row)
        self._on_edit()

def _on_delete_row(self, row: int):
    """Delete contact at specific row with confirmation."""
    contacts = self.contact_db.read_contacts()
    if row >= len(contacts):
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
```

---

## 8. Internationalization (i18n) Support

### 8.1 i18n Strategy [REQ-0045, REQ-0046]

All UI strings must use translation keys for multi-language support:

```python
# Correct (translatable):
label = QLabel(self.tr("Contact Name"))

# Incorrect (hardcoded, not translatable):
label = QLabel("Contact Name")
```

### 8.2 Translation String Locations

**File:** `app/i18n/` (i18n engine to extract strings)

**Strings to Translate:**

```
Dialog titles:
- "Add New Contact"
- "Edit Contact"

Labels:
- "Contact Name"
- "Main Nameday (MM-DD)"
- "Other Nameday (MM-DD)"
- "Recipient"
- "Email Addresses (optional)"
- "Prewritten Email (optional)"
- "Comment (optional)"
- "Disable Notifications"

Buttons:
- "Save"
- "Cancel"
- "Add Email"
- "Remove Selected"
- "Edit"
- "Delete"

Placeholders:
- "MM-DD (e.g., 12-25)"
- "Enter email address:"

Messages:
- "Name is required"
- "Main nameday is required"
- "Recipient is required"
- "Invalid email address format"
- "Invalid date format (expected MM-DD)"
- "(and all error messages)"

Dialog boxes:
- "Form Validation"
- "Data Validation"
- "Persistence Error"
- "Invalid Email"
- "No Selection"
- "Please select a contact to edit"
- "Confirm Delete"
- "Delete contact '{contact.name}'?"
- "Delete Failed"
- "Error deleting contact: {error}"
```

### 8.3 Date Format Consistency [REQ-0046]

MM-DD format is **locale-independent** by design (no locale-specific variations needed):

```python
# No locale variation: MM-DD is universal in this app
main_nameday_input.setPlaceholderText(self.tr("MM-DD (e.g., 12-25)"))

# Validation: Always MM-DD regardless of locale
# app/services/data_validator.py:
#    validate_nameday_date(date_str: str) → checks MM-DD format
```

---

## 9. Implementation Phases

### Phase 1: Create AddEditContactDialog Class ✅ (To Do)

**Deliverables:**
- New file: `app/ui/add_edit_contact_dialog.py`
- Dialog class with form layout (7 fields)
- Save/Cancel buttons
- Event handlers stubbed out

**Estimated Effort:** 2-3 hours

**Success Criteria:**
- Dialog opens without errors
- All 7 form fields visible and functional
- Save/Cancel buttons respond to clicks

---

### Phase 2: Implement Three-Layer Validation ✅ (To Do)

**Deliverables:**
- Layer 1: `_validate_fields()` method
- Layer 2: Integration with `DataValidator.validate_contact()`
- Layer 3: CRUD wiring to `ContactDatabaseManager`
- Error display via `_display_errors()`

**Estimated Effort:** 2-3 hours

**Success Criteria:**
- UI validation catches empty required fields
- DataValidator catches format errors (dates, emails)
- No database exceptions uncaught
- User sees clear error messages

---

### Phase 3: Integrate with DatabaseEditorDialog ✅ (To Do)

**Deliverables:**
- Update `DatabaseEditorDialog.__init__()` to accept `data_validator`
- Implement `_on_add()` to open ADD mode dialog
- Implement `_on_edit()` to open EDIT mode dialog
- Implement `_refresh_table()` for post-save refresh
- Add edit/delete button actions to table rows

**Estimated Effort:** 2-3 hours

**Success Criteria:**
- "Add Contact" button opens dialog in ADD mode
- Table rows have edit/delete buttons
- After successful save, table refreshes with new data
- Edited contacts reflect changes in table

---

### Phase 4: Add i18n Support ✅ (To Do)

**Deliverables:**
- Wrap all UI strings with `self.tr()`
- Document all translation strings
- Verify i18n extraction picks up all strings

**Estimated Effort:** 1-2 hours

**Success Criteria:**
- No hardcoded strings in dialog
- i18n engine can extract all translation strings
- Dialog functional in English (default locale)

---

### Phase 5: Testing & Verification ✅ (To Do)

**Deliverable:**
- Manual test scenarios covering:
  - ADD mode: Create new contact (all fields)
  - ADD mode: Validation errors
  - EDIT mode: Modify existing contact
  - EDIT mode: Email list management
  - DELETE mode: Confirm + delete
  - Refresh: Table updates after CRUD

**Estimated Effort:** 2-3 hours

**Success Criteria:**
- All CRUD operations work end-to-end
- Validation errors displayed correctly
- No data loss or corruption
- CSV file updated after operations

---

## 10. Code Template: AddEditContactDialog Skeleton

```python
# File: app/ui/add_edit_contact_dialog.py

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
    """Contact record add/edit dialog [REQ-0011, REQ-0017, REQ-0049]."""
    
    def __init__(self, contact_db_manager, data_validator,
                 contact=None, parent=None):
        """Initialize dialog in ADD or EDIT mode."""
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
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText(self.tr("Enter contact name"))
        main_layout.addWidget(QLabel(self.tr("Contact Name *")))
        main_layout.addWidget(self.name_input)
        
        self.main_nameday_input = QLineEdit()
        self.main_nameday_input.setInputMask("99-99")
        self.main_nameday_input.setPlaceholderText(self.tr("MM-DD (e.g., 12-25)"))
        main_layout.addWidget(QLabel(self.tr("Main Nameday (MM-DD) *")))
        main_layout.addWidget(self.main_nameday_input)
        
        self.recipient_input = QLineEdit()
        self.recipient_input.setPlaceholderText(self.tr("Recipient name/label"))
        main_layout.addWidget(QLabel(self.tr("Recipient *")))
        main_layout.addWidget(self.recipient_input)
        
        # Optional fields section
        self.other_nameday_input = QLineEdit()
        self.other_nameday_input.setInputMask("99-99")
        self.other_nameday_input.setPlaceholderText(self.tr("MM-DD (optional)"))
        main_layout.addWidget(QLabel(self.tr("Other Nameday (MM-DD)")))
        main_layout.addWidget(self.other_nameday_input)
        
        # Email list section
        main_layout.addWidget(QLabel(self.tr("Email Addresses")))
        self.email_list = QListWidget()
        main_layout.addWidget(self.email_list)
        
        email_button_layout = QHBoxLayout()
        add_btn = QPushButton(self.tr("Add Email"))
        add_btn.clicked.connect(self._on_add_email)
        remove_btn = QPushButton(self.tr("Remove Selected"))
        remove_btn.clicked.connect(self._on_remove_email)
        email_button_layout.addWidget(add_btn)
        email_button_layout.addWidget(remove_btn)
        email_button_layout.addStretch()
        main_layout.addLayout(email_button_layout)
        
        # Prewritten email
        main_layout.addWidget(QLabel(self.tr("Prewritten Email")))
        self.prewritten_email_input = QPlainTextEdit()
        self.prewritten_email_input.setPlaceholderText(
            self.tr("Optional email template")
        )
        main_layout.addWidget(self.prewritten_email_input)
        
        # Comment
        main_layout.addWidget(QLabel(self.tr("Comment")))
        self.comment_input = QPlainTextEdit()
        self.comment_input.setPlaceholderText(self.tr("Optional notes"))
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
    
    def _validate_fields(self) -> list:
        """Layer 1: UI field validation."""
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
        email_list = [
            self.email_list.item(i).text()
            for i in range(self.email_list.count())
        ]
        
        return Contact(
            name=self.name_input.text().strip(),
            main_nameday=self.main_nameday_input.text().strip(),
            recipient=self.recipient_input.text().strip(),
            other_nameday=self.other_nameday_input.text().strip() or None,
            email_addresses=email_list,
            prewritten_email=self.prewritten_email_input.toPlainText().strip() or None,
            comment=self.comment_input.toPlainText().strip() or None,
            notification_disabled=self.notification_disabled_checkbox.isChecked()
        )
    
    def _display_errors(self, errors: list, title: str = "Error"):
        """Display error messages to user."""
        message = "\n".join([f"• {e}" for e in errors])
        QMessageBox.warning(
            self,
            title,
            self.tr(f"Please correct the following:\n\n{message}"),
            QMessageBox.Ok
        )
    
    def _validate_and_save(self) -> bool:
        """Three-layer validation and persistence."""
        # Layer 1: UI validation
        ui_errors = self._validate_fields()
        if ui_errors:
            self._display_errors(ui_errors, self.tr("Form Validation"))
            return False
        
        # Build Contact object
        contact = self._build_contact_from_form()
        
        # Layer 2: Business logic validation
        validation_errors = self.validator.validate_contact(contact)
        if validation_errors:
            self._display_errors(validation_errors, self.tr("Data Validation"))
            return False
        
        # Layer 3: Persistence
        try:
            if self.is_edit_mode:
                self.contact_db.update_contact(self.contact.name, contact)
            else:
                self.contact_db.create_contact(contact)
            
            self.accept()
            return True
        except (ValidationException, DatabaseException) as e:
            self._display_errors(
                [str(e)],
                self.tr("Database Error")
            )
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
            self.email_list.takeItem(current)
```

---

## 11. Integration Checklist

- [ ] Create `app/ui/add_edit_contact_dialog.py` with full implementation
- [ ] Update `DatabaseEditorDialog.__init__()` to accept `data_validator`
- [ ] Implement `DatabaseEditorDialog._on_add()`
- [ ] Implement `DatabaseEditorDialog._on_edit()`
- [ ] Implement `DatabaseEditorDialog._refresh_table()`
- [ ] Implement `DatabaseEditorDialog._create_action_buttons()`
- [ ] Implement `DatabaseEditorDialog._on_edit_row()`
- [ ] Implement `DatabaseEditorDialog._on_delete_row()`
- [ ] Add "Edit" button to table row actions
- [ ] Update `app/ui/system_tray.py` to pass `data_validator` to `DatabaseEditorDialog`
- [ ] Wrap all strings with `self.tr()` for i18n
- [ ] Test all CRUD operations end-to-end
- [ ] Verify CSV persistence after operations
- [ ] Test delete confirmation dialog
- [ ] Test validation error scenarios
- [ ] Verify column width persistence still works after table refresh

---

## 12. File Locations & Dependencies

| Component | File | Status |
|-----------|------|--------|
| New Dialog Class | `app/ui/add_edit_contact_dialog.py` | ✅ To Create |
| CRUD Backend | `app/managers/contact_db_manager.py` | ✅ Already Exists |
| Validation | `app/services/data_validator.py` | ✅ Already Exists |
| Integration Point | `app/ui/database_editor_dialog.py` | 📝 To Update |
| System Tray Integration | `app/ui/system_tray.py` | 📝 To Update |
| i18n Support | `app/i18n/` | 📝 To Populate |

---

## 13. Success Criteria & Acceptance Tests

**Test Scenario 1: Add New Contact (All Fields)**
```gherkin
Given: Database editor is open
When: User clicks "Add Contact"
Then: Add Contact dialog opens in empty state
And: All 7 form fields are visible and editable
And: Required fields marked with *
When: User enters all fields with valid data
And: Clicks Save
Then: Three-layer validation passes
And: Contact persisted to CSV
And: Dialog closes
And: Table refreshes showing new contact
```

**Test Scenario 2: Validation Errors**
```gherkin
Given: Add Contact dialog is open
When: User leaves Name field empty
And: Clicks Save
Then: Layer 1 validation catches missing Name
And: Error displayed: "Name is required"
And: Dialog remains open
When: User enters invalid date "13-45" in Main Nameday
And: Clicks Save
Then: Layer 2 validation catches format error
And: Error displayed: "Invalid date format (expected MM-DD)"
And: Dialog remains open
```

**Test Scenario 3: Edit Existing Contact**
```gherkin
Given: Database editor is open with contacts
And: User selects a contact row
When: User clicks "Edit"
Then: Edit Contact dialog opens
And: All fields pre-populated with contact data
And: Email list shows all addresses
When: User modifies comment field
And: Clicks Save
Then: Contact updated in CSV
And: Table refreshes showing updated comment
And: Dialog closes
```

**Test Scenario 4: Email List Management**
```gherkin
Given: Add Contact dialog is open
When: User clicks "Add Email"
Then: Text input dialog appears
When: User enters "user@example.com"
Then: Email added to list
And: Email validated against format
When: User enters invalid email "not-an-email"
Then: Validation error shown
And: Email not added to list
When: User selects email and clicks "Remove Selected"
Then: Email removed from list
```

**Test Scenario 5: Delete Contact with Confirmation**
```gherkin
Given: Database editor is open with contacts
When: User clicks Delete button on row
Then: Confirmation dialog: "Delete contact 'John'?"
When: User clicks Yes
Then: Contact deleted from CSV
And: Table refreshed
And: Row removed
When: Delete is clicked and user cancels
Then: Contact remains in database
```

---

## 14. References & Related Documentation

- **Requirements Document:** `Docs/requirements.md` (REQ-0011, REQ-0017, REQ-0029–REQ-0040, REQ-0045–REQ-0046, REQ-0049)
- **System Design:** `Docs/system_design.md` (Manager classes, data persistence)
- **Type Definitions:** `app/types.py` (Contact dataclass, field definitions)
- **CRUD Backend:** `app/managers/contact_db_manager.py` (create/update/delete operations)
- **Validation:** `app/services/data_validator.py` (Business logic validation)
- **Existing Dialog Pattern:** `app/ui/database_editor_dialog.py` (Column width management example)
- **Column Width Implementation:** `Docs/impl_contact_db_dditionals.md` (UI dialog pattern reference)

---

## 15. Notes & Assumptions

1. **Data Validator Injection:** `DataValidator` instance must be injected through `DatabaseEditorDialog.__init__()` for accessibility in child dialog. If this breaks existing instantiation, update `system_tray.py` to pass instance.

2. **Contact Identity in Edit Mode:** Edit dialog uses `original_name` field to identify which contact to update. If users can change names, use a unique ID (not implemented yet per requirements).

3. **Email List Management:** Email addresses are stored as comma/semicolon-separated in CSV (per Contact dataclass), but UI manages as list for user-friendliness. Conversion handled in `_build_contact_from_form()`.

4. **Column Width Persistence After Refresh:** When `_refresh_table()` is called, ensure `_load_column_widths_from_config()` is NOT re-executed (widths already set at init). Only table data should refresh.

5. **MM-DD Format Isolation:** Date format is entirely MM-DD (no locale variants per REQ-0046). All validation and UI assumes this format.

6. **Internationalization Rollout:** All UI strings ready for translation extraction (via `self.tr()`), but actual translations added post-implementation.

---

**Document End**
