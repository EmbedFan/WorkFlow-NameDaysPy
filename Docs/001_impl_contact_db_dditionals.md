# Implementation Plan: Database Column Width Management
## REQ-0056 to REQ-0060

**Document Version:** 1.0  
**Date:** April 1, 2026  
**Target Component:** `app/ui/database_editor_dialog.py`  
**Related Components:** `app/managers/settings_manager.py`, `config/config.json`

---

## Overview

This implementation plan covers five interrelated requirements for managing column widths in the Database Editor Dialog:

- **REQ-0056**: Database Column Resizability - Enable mouse-driven column width adjustments for all columns
- **REQ-0057**: Auto-Fit Column Width - Auto-size Name, Main Nameday, Other Nameday, Recipient, Email, Disabled, Actions columns to fit data
- **REQ-0058**: Comment Column Manual Width Adjustment - Allow user control over Comment column (not auto-fitted)
- **REQ-0059**: Column Width Configuration Persistence - Save widths for Name, Recipient, Other Nameday, Email, Comment to config.json
- **REQ-0060**: Column Width Configuration Restoration - Restore saved widths on initialization

---

## Technical Approach

### Architecture Overview

```
┌─────────────────────────────────────────────┐
│   DatabaseEditorDialog (PyQt5)              │
│   ┌─────────────────────────────────────┐   │
│   │  QTableWidget                       │   │
│   │  ├─ Column Headers (resizable)      │   │
│   │  ├─ Dynamic Width Management        │   │
│   │  └─ Mouse Event Handling            │   │
│   └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘
              │                       │
              ▼                       ▼
    ┌──────────────────┐    ┌──────────────────┐
    │  SettingsManager │    │  Config Handler  │
    │  Load/Save       │    │  JSON I/O        │
    │  Column Widths   │    │  Persistence     │
    └──────────────────┘    └──────────────────┘
              │
              ▼
    ┌──────────────────┐
    │  config.json     │
    │  Column Widths   │
    │  Mapping         │
    └──────────────────┘
```

### Key Design Decisions

1. **Resize Mode**: Replace `QHeaderView.Stretch` with `QHeaderView.Interactive` to enable manual resizing on all columns
2. **Auto-Fit Strategy**: Apply auto-fit on dialog initialization for 7 columns (Name, Main Nameday, Other Nameday, Recipient, Email, Disabled, Actions)
3. **Comment Column**: Resizable but NOT auto-fitted; purely user-controlled width
4. **Persistence Scope**: Only 5 columns persisted to config (Name, Recipient, Other Nameday, Email, Comment); others auto-fit on each load
5. **Persistence Layer**: Use `SettingsManager` to handle column width I/O
6. **Config Structure**: Store widths in `config.json` under `"database_editor.column_widths"` section with column names as keys (5 items only)

---

## Implementation Steps

### Phase 1: Configuration Structure Setup

#### Step 1.1: Define Config Schema
Add to `config/config.json`:
```json
{
  "database_editor": {
    "column_widths": {
      "Name": 150,
      "Recipient": 150,
      "Other Nameday": 100,
      "Email": 180,
      "Comment": 200
    }
  }
}
```

**Note:** Only these 5 columns are persisted to config. Main Nameday (col 1), Disabled (col 6), and Actions (col 7) are auto-fitted but NOT saved.

#### Step 1.2: Update SettingsManager
Extend `app/managers/settings_manager.py` with methods:
- `get_column_width(column_name: str) -> int`
- `set_column_width(column_name: str, width: int) -> None`
- `get_all_column_widths() -> dict`
- `save_column_widths(widths_dict: dict) -> None`

**Acceptance Criteria:**
- Methods handle missing config gracefully
- Returns default values if config section absent
- Persists changes to config.json immediately

---

### Phase 2: UI Modification - DatabaseEditorDialog

#### Step 2.1: Modify Header Resize Mode (REQ-0056)
**Location:** `app/ui/database_editor_dialog.py` - `_setup_ui()` method

**Current Code:**
```python
self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
```

**New Code:**
```python
# Enable manual column resizing (REQ-0056)
self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
```

**Acceptance Criteria:**
- Columns are resizable by dragging header borders
- Resize handles appear on mouse hover
- Column width changes respond immediately to drag

#### Step 2.2: Implement Auto-Fit Logic (REQ-0057)
**Location:** `app/ui/database_editor_dialog.py` - new method `_auto_fit_columns()`

**Implementation:**
```python
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
```

**Acceptance Criteria:**
- Name, Main Nameday, Other Nameday, Recipient, Email, Disabled, Actions columns auto-fit on initialization
- Columns sized appropriately for content visibility
- Comment column (col 5) NOT auto-fitted (user controlled)
- All auto-fitted columns visually clean without truncation

#### Step 2.3: Load Saved Column Widths (REQ-0060)
**Location:** `app/ui/database_editor_dialog.py` - modify `_setup_ui()` method

**Implementation:**
```python
def _load_column_widths_from_config(self):
    """Load column widths from configuration [REQ-0060]."""
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
```

**Acceptance Criteria:**
- Reads widths from config.json on dialog open
- Applies widths to corresponding columns (0-7: Name, Main Nameday, Other Nameday, Recipient, Email, Comment, Disabled, Actions)
- Falls back to auto-fit if config missing or corrupted
- Logs load operations for debugging
- Handles all 8 columns correctly

#### Step 2.4: Save Column Widths on Dialog Close (REQ-0059)
**Location:** `app/ui/database_editor_dialog.py` - override `closeEvent()` method

**Implementation:**
```python
def closeEvent(self, event):
    """Save column widths when dialog closes [REQ-0059].
    
    Saves widths for: Name, Recipient, Other Nameday, Email, Comment
    (not: Main Nameday, Disabled, Actions which are auto-fitted)
    """
    try:
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
        logger.error(f"Failed to save column widths: {e}")
    
    super().closeEvent(event)
```

**Acceptance Criteria:**
- Widths captured when user closes dialog
- Configurable columns saved (Name, Recipient, Other Nameday, Email, Comment)
- Auto-fitted columns (Main Nameday, Disabled, Actions) not saved to config
- Config.json updated immediately
- Handles errors gracefully without blocking close

---

### Phase 3: Integration Updates

#### Step 3.1: Update DatabaseEditorDialog Constructor
**Inject SettingsManager dependency:**

```python
def __init__(self, contact_db, settings_manager, parent=None):
    super().__init__(parent)
    self.contact_db = contact_db
    self.settings_manager = settings_manager  # NEW
    
    self.setWindowTitle("Contact Database")
    self.setGeometry(100, 100, 800, 500)
    self._setup_ui()
```

#### Step 3.2: Update UI Setup Sequence
**Modify `_setup_ui()` to call width management methods in order:**

```python
def _setup_ui(self):
    """Setup UI components."""
    layout = QVBoxLayout()
    
    # Create table with 8 columns
    self.table = QTableWidget()
    self.table.setColumnCount(8)
    self.table.setHorizontalHeaderLabels([
        "Name",              # 0 - Resizable, Saved
        "Main Nameday",      # 1 - Auto-fitted only (not saved)
        "Other Nameday",     # 2 - Resizable, Saved
        "Recipient",         # 3 - Resizable, Saved
        "Email",             # 4 - Resizable, Saved
        "Comment",           # 5 - Resizable, Saved (user control)
        "Disabled",          # 6 - Auto-fitted only (not saved)
        "Actions"            # 7 - Auto-fitted only (not saved)
    ])
    
    # Set header resize mode to interactive (REQ-0056)
    self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
    
    # Populate table with contacts
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
        # Column 7 (Actions) typically contains buttons, handled separately
    
    layout.addWidget(self.table)
    
    # Apply widths in order: config → auto-fit
    config_loaded = self._load_column_widths_from_config()  # REQ-0060
    if not config_loaded:
        self._auto_fit_columns()  # REQ-0057 (fallback)
    
    # ... rest of UI setup (buttons, etc) ...
```

**Column Mapping:**
| Index | Column Name | Auto-Fit | Saved | User Resize |
|-------|-------------|----------|-------|-------------|
| 0 | Name | ✅ | ✅ | ✅ |
| 1 | Main Nameday | ✅ | ❌ | ✅ |
| 2 | Other Nameday | ✅ | ✅ | ✅ |
| 3 | Recipient | ✅ | ✅ | ✅ |
| 4 | Email | ✅ | ✅ | ✅ |
| 5 | Comment | ❌ | ✅ | ✅ |
| 6 | Disabled | ✅ | ❌ | ✅ |
| 7 | Actions | ✅ | ❌ | ✅ |

---

## Configuration Structure

### config.json Schema Extension
```json
{
  "app": { ... },
  "email": { ... },
  "database_editor": {
    "column_widths": {
      "Name": 180,
      "Recipient": 180,
      "Other Nameday": 120,
      "Email": 220,
      "Comment": 250
    }
  }
}
```

**Note:** Main Nameday (col 1), Disabled (col 6), and Actions (col 7) are auto-fitted but NOT persisted to config. Only Name, Recipient, Other Nameday, Email, Comment widths are saved per REQ-0059.

### Default Widths (Fallback)
```python
DEFAULT_COLUMN_WIDTHS = {
    "Name": 150,
    "Recipient": 150,
    "Other Nameday": 100,
    "Email": 180,
    "Comment": 200
}
```

---

## Implementation Checklist

### Code Changes
- [ ] Update `app/managers/settings_manager.py` with column width methods
- [ ] Modify `app/ui/database_editor_dialog.py`:
  - [ ] Change `setSectionResizeMode()` to Interactive
  - [ ] Add `_auto_fit_columns()` method
  - [ ] Add `_load_column_widths_from_config()` method
  - [ ] Override `closeEvent()` for saving
  - [ ] Update constructor to accept `settings_manager`
  - [ ] Update `_setup_ui()` method call sequence
- [ ] Update `config/config.json` with initial column widths schema

### Testing Requirements
- [ ] Manual Tests:
  - [ ] Drag column headers to resize all columns (REQ-0056)
  - [ ] Verify auto-fit on first open for Name, Main Nameday, Other Nameday, Recipient, Email, Disabled, Actions (REQ-0057)
  - [ ] Verify Comment column NOT auto-fitted but resizable (REQ-0058)
  - [ ] Close and reopen dialog - saved widths persist (REQ-0059, REQ-0060)
  - [ ] Delete config section - auto-fit applied as fallback (REQ-0060)
  
- [ ] Edge Cases:
  - [ ] Window too narrow - columns overflow gracefully
  - [ ] Empty database - auto-fit uses headers only
  - [ ] Very long content - columns expand appropriately
  - [ ] Missing column in config - uses default/auto-fit
  - [ ] Negative width in config - rejected as invalid
  - [ ] All 8 columns resizable
  - [ ] Only 5 columns (Name, Recipient, Other Nameday, Email, Comment) saved to config

### Documentation Updates
- [ ] Update `README.md` with user instructions for column resizing
- [ ] Add inline comments to `database_editor_dialog.py` linking to REQs (REQ-0056, REQ-0057, REQ-0058, REQ-0059, REQ-0060)
- [ ] Document config.json schema with column mapping (which columns are saved vs auto-fitted)
- [ ] Add docstrings to all new methods with REQ references
- [ ] Document column index mapping in code comments (0=Name, 1=Main Nameday, etc.)

---

## Risks and Mitigation

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|-----------|
| Column widths too narrow for content | Poor UX, text cut off | Medium | Implement sensible minimum widths; test with various content |
| Config corruption loses widths | User loses preferences | Low | Validate widths on load; fall back to defaults |
| Very small window makes columns overlap | Layout breaks | Medium | Set minimum window width or implement horizontal scrollbar |
| Auto-fit takes too long with large DB | UI freeze on open | Low | Optimize auto-fit algorithm; limit row count for width calculation |
| Column width state not saved on crash | Widths lost | Low | Save widths immediately on each resize (optional enhancement) |

---

## Testing Strategy

### Unit Tests (Recommended)
```python
# test_settings_manager.py
def test_get_column_width():
    """Test retrieval of column width from config."""
    
def test_save_column_widths():
    """Test saving widths to config.json."""
    
def test_default_widths_on_missing_config():
    """Test fallback to defaults when config missing."""

# test_database_editor_dialog.py
def test_column_widths_loaded_from_config():
    """Test widths applied from config on init."""
    
def test_column_widths_saved_on_close():
    """Test widths persisted when dialog closes."""
    
def test_auto_fit_columns():
    """Test auto-fit sizing for content columns."""
```

### Integration Tests
1. Open dialog → verify config widths applied
2. Resize column → close dialog → open dialog → verify width persisted
3. Delete config section → open dialog → verify auto-fit applied
4. Add rows with long content → verify column widths accommodate

### Manual Testing Checklist
- [ ] Drag column borders to resize smoothly
- [ ] Close and reopen - widths match previous session
- [ ] Comment column resizable independently
- [ ] Auto-fit works with various content lengths
- [ ] Config.json updated after closing dialog
- [ ] App recovers gracefully if config corrupted

---

## Implementation Dependencies

### Required Changes
1. **Settings Manager** - Column width load/save methods (supports 5 persistent columns)
2. **Database Editor Dialog** - Resize mode, auto-fit for 7 columns, persistence for 5 columns
3. **Config.json** - Column width schema with 5 column mapping

### Column Persistence Strategy
- **Auto-fitted (not persisted):** Main Nameday (1), Disabled (6), Actions (7)
- **Both auto-fit and persisted:** Name (0), Other Nameday (2), Recipient (3), Email (4)
- **Manual only (not auto-fit, but persisted):** Comment (5)

### Optional Enhancements
- Save widths on each resize (not just on close) for real-time config updates
- Per-column minimum width validation to prevent UI degradation
- Column width reset to defaults button in settings
- Column reorder persistence
- Width animation on resize for visual feedback

---

## Success Criteria (Acceptance)

✅ **REQ-0056**: User can drag column headers to adjust width for all columns; resize is smooth and immediate  
✅ **REQ-0057**: Name, Main Nameday, Other Nameday, Recipient, Email, Disabled, Actions columns auto-fit to longest content on first open  
✅ **REQ-0058**: Comment column is resizable and NOT auto-fitted; user has full control  
✅ **REQ-0059**: Column widths for Name, Recipient, Other Nameday, Email, Comment saved to config.json when dialog closes  
✅ **REQ-0060**: Saved widths restored from config on dialog initialization; defaults/auto-fit used if config missing  

---

## Estimated Effort

| Phase | Task | Complexity | Hours |
|-------|------|-----------|-------|
| 1 | Config structure, SettingsManager updates | Low | 1.5 |
| 2 | UI modifications, auto-fit, persistence | Medium | 3 |
| 3 | Integration, constructor updates | Low | 1 |
| Testing | Unit, integration, manual testing | Medium | 2 |
| **Total** | | | **7.5** |

---

## References
- PyQt5 QTableWidget Documentation
- PyQt5 QHeaderView Resize Modes
- Existing `SettingsManager` implementation
- REQ-0056, REQ-0057, REQ-0058, REQ-0059, REQ-0060 in `Docs/requirements.md`
