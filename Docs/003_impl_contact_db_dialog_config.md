# Contact Database Dialog Size and Column Width Persistence
## Implementation Plan

**Document:** `003_impl_contact_db_dialog_config.md`  
**Status:** Implementation Specification  
**Date:** 2026-04-02  
**Related Requirements:** REQ-0061, REQ-0062, REQ-0063  
**Based on Decisions:**
- Default dialog size: 900x600
- No window position/maximized state saving
- Persist 5 columns; auto-fit remaining 3
- Config structure: `database_editor.window.width/height`
- Invalid config fallback: defaults + auto-fit

---

## 1. Overview

This implementation adds dialog window size persistence and improves column width restoration logic for the Contact Database dialog (DatabaseEditorDialog).

### Current State
- ✅ Column widths saved/restored (REQ-0059, REQ-0060)
- ⚠️ Dialog size NOT persisted (always 900x600)
- ⚠️ Auto-fit always runs even when config exists
- ❌ No optimized column width loading

### Target State
- ✅ Dialog size (width/height) saved on close and restored on open
- ✅ Column width loading skips auto-fit when config exists (performance)
- ✅ Fallback to defaults when config missing or corrupted
- ✅ Clear separation: config-driven OR auto-fit, never both

---

## 2. Requirements Summary

| Req ID | Title | Scope |
|--------|-------|-------|
| **REQ-0061** | Dialog Size Persistence | Save/restore dialog width & height, not position |
| **REQ-0062** | Column Width Optimization | Skip auto-fit when config exists; persist 5 columns only |
| **REQ-0063** | Error Handling & Fallback | Graceful fallback on invalid/missing config |

### Key Decisions Locked In
1. **Default Size:** 900w x 600h
2. **No Position Saving:** Multi-monitor safety
3. **No Maximized State:** Deferred to v2
4. **Column Scope:** 5 persist (Name, Other Nameday, Recipient, Email, Comment) + 3 auto-fit (Main Nameday, Disabled, Actions)
5. **Config Path:** `database_editor.window.width` and `database_editor.window.height`
6. **Auto-Fit Logic:** Use config OR auto-fit, never mix

---

## 3. Architecture & Design

### 3.1 Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│ Dialog Open (DatabaseEditorDialog.__init__)                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────────┐
        │ Load Config Values:    │
        │ - window.width/height  │
        │ - column_widths[5]     │
        └────┬───────────────────┘
             │
             ├─ Config Valid? ─────No─────┐
             │                             │
             │ Yes                         ▼
             │                    ┌──────────────────┐
             ▼                    │ Use Defaults:    │
        ┌─────────────────────┐   │ - Size: 900x600  │
        │ Apply Config:       │   │ - Auto-fit cols  │
        │ - setGeometry()     │   └──────────────────┘
        │ - setColumnWidths   │
        │ - SKIP Auto-Fit     │
        └────┬────────────────┘
             │
             └──────┬──────────────────────────────┐
                    │                              │
                    ▼                              ▼
             [Dialog Ready]                [Dialog Ready]
             (Config-driven)           (Default + Auto-fit)
```

### 3.2 Config File Structure

**Current:**
```json
{
  "database_editor": {
    "column_widths": {
      "Name": 150,
      "Other Nameday": 100,
      "Recipient": 150,
      "Email": 180,
      "Comment": 200
    }
  }
}
```

**After Implementation:**
```json
{
  "database_editor": {
    "window": {
      "width": 900,
      "height": 600
    },
    "column_widths": {
      "Name": 150,
      "Other Nameday": 100,
      "Recipient": 150,
      "Email": 180,
      "Comment": 200
    }
  }
}
```

### 3.3 Column Mapping

| Column Index | Column Name | Persist? | Auto-Fit? | Notes |
|---|---|---|---|---|
| 0 | Name | ✅ Yes | ❌ No | User-resizable, config-driven |
| 1 | Main Nameday | ❌ No | ✅ Yes | Always auto-fit, never saved |
| 2 | Other Nameday | ✅ Yes | ❌ No | User-resizable, config-driven |
| 3 | Recipient | ✅ Yes | ❌ No | User-resizable, config-driven |
| 4 | Email | ✅ Yes | ❌ No | User-resizable, config-driven |
| 5 | Comment | ✅ Yes | ❌ No | User-resizable (REQ-0058), config-driven |
| 6 | Disabled | ❌ No | ✅ Yes | Always auto-fit, never saved |
| 7 | Actions | ❌ No | ✅ Yes | Always auto-fit, never saved |

---

## 4. Implementation Phases

### Phase 1: Update Config Structure & SettingsManager ✅ (To Do)

**Objective:** Add helper methods for dialog config I/O

**Files to Modify:**
- `app/managers/settings_manager.py`

**Changes:**
1. Add method: `get_dialog_window_size() -> Tuple[int, int]`
   - Returns (width, height) from config
   - Validates values > 0
   - Defaults to (900, 600) if missing/invalid

2. Add method: `save_dialog_window_size(width: int, height: int) -> None`
   - Takes width and height
   - Saves to `database_editor.window.width` and `.height`
   - Creates section if missing
   - Validates before saving

3. Add method: `get_dialog_column_widths() -> dict`
   - Returns column widths dict from config
   - Validates all values > 0
   - Returns empty dict if missing/invalid (triggers auto-fit)

4. Enhance existing: `save_column_widths(widths_dict: dict) -> None`
   - Already exists per REQ-0059
   - No changes needed

**Validation Rules:**
- Width/height must be integers > 0 and < 10000 (reasonable bounds)
- If any value invalid: return defaults
- Log warnings for invalid config

**Code Example:**
```python
def get_dialog_window_size(self) -> Tuple[int, int]:
    """Get saved dialog window size from config [REQ-0061].
    
    Returns:
        Tuple of (width, height). Defaults to (900, 600) if missing/invalid.
    """
    try:
        window_config = self.settings.get("database_editor", {}).get("window", {})
        width = window_config.get("width")
        height = window_config.get("height")
        
        # Validate
        if (isinstance(width, int) and isinstance(height, int) and
            0 < width < 10000 and 0 < height < 10000):
            return (width, height)
        
        logger.warning(f"Invalid dialog window config: {window_config}, using defaults")
        return (900, 600)
    except Exception as e:
        logger.error(f"Error reading dialog window config: {e}")
        return (900, 600)

def save_dialog_window_size(self, width: int, height: int) -> None:
    """Save dialog window size to config [REQ-0061].
    
    Args:
        width: Dialog width in pixels
        height: Dialog height in pixels
    """
    try:
        # Validate
        if not (isinstance(width, int) and isinstance(height, int) and
                0 < width < 10000 and 0 < height < 10000):
            logger.warning(f"Skipping invalid window size: {width}x{height}")
            return
        
        # Ensure path exists
        if "database_editor" not in self.settings:
            self.settings["database_editor"] = {}
        if "window" not in self.settings["database_editor"]:
            self.settings["database_editor"]["window"] = {}
        
        # Save
        self.settings["database_editor"]["window"]["width"] = width
        self.settings["database_editor"]["window"]["height"] = height
        
        self.write_json()
        logger.info(f"Saved dialog window size: {width}x{height}")
    except Exception as e:
        logger.error(f"Failed to save dialog window size: {e}")
```

---

### Phase 2: Update DatabaseEditorDialog - Load Logic ✅ (To Do)

**Objective:** Load and apply saved dialog size and column widths on initialization

**Files to Modify:**
- `app/ui/database_editor_dialog.py`

**Changes:**

1. **Update `__init__()` method:**
   - Load dialog size early (before setup_ui)
   - Call `_load_dialog_config()` method
   - Store config loaded state for later use

2. **New method: `_load_dialog_config() -> dict`**
   - Get saved window size via `settings_manager.get_dialog_window_size()`
   - Get saved column widths via `settings_manager.get_dialog_column_widths()`
   - Apply window size: `self.setGeometry(0, 0, width, height)` (position 0,0 = default/centered by OS)
   - Return dict: `{"column_widths_available": bool, "window_size": (w, h)}`
   - If window size valid: set it immediately
   - If invalid: use default 900x600

3. **Update `_setup_ui()` method:**
   - After creating table, check if column widths were loaded
   - **If widths loaded from config:**
     - Skip `_auto_fit_columns()` call completely
     - Call `_apply_loaded_column_widths()` instead
   - **If no config widths or invalid:**
     - Call `_auto_fit_columns()` as fallback (existing logic)

4. **New method: `_apply_loaded_column_widths(widths: dict)`**
   - Take dictionary of column name → width mappings
   - Iterate through table columns (0-7)
   - Look up saved width in dict by column name
   - Apply width via `self.table.setColumnWidth(col_index, width)`
   - Log success for each column

**Code Example:**
```python
def _load_dialog_config(self) -> dict:
    """Load dialog size and column widths from config [REQ-0061, REQ-0062].
    
    Returns:
        Dict with keys: column_widths_available (bool), window_size (tuple)
    """
    # Load window size
    width, height = self.settings_manager.get_dialog_window_size()
    self.setGeometry(0, 0, width, height)
    logger.info(f"Loaded dialog size from config: {width}x{height}")
    
    # Load column widths
    widths = self.settings_manager.get_dialog_column_widths()
    has_widths = bool(widths)  # True if dict non-empty
    
    return {
        "column_widths_available": has_widths,
        "column_widths": widths,
        "window_size": (width, height)
    }

def _setup_ui(self):
    """Setup UI components [REQ-0011, REQ-0049]."""
    layout = QVBoxLayout()
    
    # Table setup
    self.table = QTableWidget()
    self.table.setColumnCount(8)
    self.table.setHorizontalHeaderLabels([...])
    self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
    
    # Refresh table data
    self._refresh_table()
    
    layout.addWidget(self.table)
    
    # Load config
    config_state = self._load_dialog_config()
    
    # Apply column widths: config first, then auto-fit fallback [REQ-0062]
    if config_state["column_widths_available"]:
        self._apply_loaded_column_widths(config_state["column_widths"])
        logger.info("Applied column widths from config [REQ-0062]")
    else:
        self._auto_fit_columns()
        logger.info("Auto-fitted columns (no config available) [REQ-0057]")
    
    # Buttons...
    button_layout = QHBoxLayout()
    # ... button setup ...
    layout.addLayout(button_layout)
    
    self.setLayout(layout)

def _apply_loaded_column_widths(self, widths: dict):
    """Apply column widths loaded from config [REQ-0062].
    
    Args:
        widths: Dict of {column_name: width_pixels}
    """
    column_mapping = {
        0: "Name",
        2: "Other Nameday",
        3: "Recipient",
        4: "Email",
        5: "Comment"
    }
    
    for col_index, col_name in column_mapping.items():
        if col_name in widths and widths[col_name] > 0:
            self.table.setColumnWidth(col_index, widths[col_name])
            logger.info(f"Applied saved width for {col_name}: {widths[col_name]}px")
        else:
            logger.warning(f"No valid width for column {col_name}, skipping")
```

---

### Phase 3: Update DatabaseEditorDialog - Save Logic ✅

**Objective:** Persist dialog size and column widths on dialog close (ALL close methods)

**Files to Modify:**
- `app/ui/database_editor_dialog.py`

**Key Pattern:** Use shared `_save_dialog_config()` helper method so configuration saves work for BOTH:
- Close button click
- System X button (via closeEvent)

**Changes:**

1. **New helper method: `_save_dialog_config()`**
   - Extract save logic (window size + column widths) into centralized method
   - Called from both `_on_close()` and `closeEvent()`
   - Prevents code duplication and ensures consistent behavior

2. **New button handler: `_on_close()`**
   - Called when Close button is clicked
   - Calls `_save_dialog_config()` to persist config
   - Then calls `self.accept()` to close dialog

3. **Update Close button connection:**
   - Change from: `close_btn.clicked.connect(self.accept)`
   - Change to: `close_btn.clicked.connect(self._on_close)`

4. **Update `closeEvent()` method:**
   - Existing column width save logic: extracted to helper
   - Calls `_save_dialog_config()` helper
   - Then calls `super().closeEvent(event)`

**Code Example:**
```python
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

def closeEvent(self, event):
    """Save dialog configuration when dialog closes via system X button [REQ-0059, REQ-0061].
    
    Calls shared _save_dialog_config() helper so both Close button and system X button
    save the dialog configuration.
    """
    self._save_dialog_config()
    super().closeEvent(event)
```

---

## 5. Implementation Checklist

### Phase 1: SettingsManager
- [ ] Add `get_dialog_window_size() -> Tuple[int, int]` method
- [ ] Add `save_dialog_window_size(width, height)` method
- [ ] Add validation (values > 0 and < 10000)
- [ ] Add logging for invalid config
- [ ] Handle missing `database_editor.window` section
- [ ] Test: retrieving defaults when config missing
- [ ] Test: retrieving saved values when config exists
- [ ] Test: validation rejects invalid values

### Phase 2: DatabaseEditorDialog - Load Logic
- [ ] Add `_load_dialog_config() -> dict` method
- [ ] Update `__init__()` to call load method
- [ ] Update `_setup_ui()` to check config state
- [ ] Add `_apply_loaded_column_widths(widths)` method
- [ ] Implement logic: use config OR auto-fit (never both)
- [ ] Add logging at each step
- [ ] Test: load saved size on dialog open
- [ ] Test: skip auto-fit when config exists
- [ ] Test: use auto-fit when config missing
- [ ] Test: use auto-fit when config invalid

### Phase 3: DatabaseEditorDialog - Save Logic
- [ ] New method: `_save_dialog_config()` - centralized save logic for window size + column widths
- [ ] New method: `_on_close()` - button handler that saves config then accepts dialog
- [ ] Update Close button connection: `close_btn.clicked.connect(self._on_close)` (not self.accept)
- [ ] Update `closeEvent()` to call `_save_dialog_config()` helper
- [ ] Verify: save works for Close button click
- [ ] Verify: save works for system X button click
- [ ] Test: size restored after close/reopen

---

## 6. Testing Scenarios

### Scenario 1: First Launch (No Config Exists)
```
Pre-condition: database_editor.window section missing from config.json
Steps:
  1. Launch app
  2. Open Contact Database dialog
Expected:
  ✅ Dialog size: 900x600 (default)
  ✅ Columns auto-fitted (no config available)
  ✅ Log: "No saved dialog config, using defaults"
  ✅ Config creates database_editor.window section with size on close
```

### Scenario 2: Restore Saved Size and Widths
```
Pre-condition: Config exists with:
  - database_editor.window: {width: 1000, height: 700}
  - database_editor.column_widths: {Name: 200, Recipient: 150, ...}
Steps:
  1. Launch app
  2. Open Contact Database dialog
Expected:
  ✅ Dialog opens with size 1000x700
  ✅ Columns load from config (Name: 200, Recipient: 150, ...)
  ✅ Auto-fit NOT called (log should NOT show "Auto-fitted" message)
  ✅ 3 auto-fit columns still auto-fitted
Verification:
  - Check logs: "Applied column widths from config"
  - Check logs: NO "Auto-fitted columns" message
```

### Scenario 3: Resize and Verify Save
```
Pre-condition: Dialog open with restored size
Steps:
  1. User manually resizes dialog to 1200x800
  2. User resizes some columns (e.g., Name to 250px)
  3. User closes dialog
Expected:
  ✅ On close: new size 1200x800 saved to config
  ✅ On close: new column widths saved
  ✅ Log: "Saved dialog size: 1200x800"
Verification:
  1. Close and reopen dialog
  2. Dialog should be 1200x800
  3. Name column should be 250px
```

### Scenario 4: Invalid Config Fallback
```
Pre-condition: Config has invalid values:
  - database_editor.window: {width: -100, height: "invalid"}
  - database_editor.column_widths: {Name: 0, ...}
Steps:
  1. Launch app
  2. Open Contact Database dialog
Expected:
  ✅ Dialog ignores invalid config
  ✅ Dialog size: 900x600 (default)
  ✅ Columns auto-fitted (config invalid, triggering auto-fit)
  ✅ Log: "Invalid dialog window config, using defaults"
  ✅ Log: "Invalid column widths, applying auto-fit"
Verification:
  - Verify dialog is 900x600
  - Verify all 8 columns are auto-fitted
```

### Scenario 5: Partial Config (Only Size, No Widths)
```
Pre-condition: Config has window size but no column_widths section
  - database_editor.window: {width: 950, height: 650}
  - database_editor.column_widths: missing
Steps:
  1. Launch app
  2. Open Contact Database dialog
Expected:
  ✅ Dialog size: 950x650 (config exists)
  ✅ Columns auto-fitted (no column_widths in config)
Verification:
  - Dialog is 950x650
  - Columns are auto-fitted (not from saved widths)
```

### Scenario 6: 3 Auto-Fit Columns Not Persisted
```
Pre-condition: Dialog open with custom column widths saved
Steps:
  1. User resizes Main Nameday (col 1) to 250px
  2. User resizes Disabled (col 6) to 100px
  3. User closes dialog
Expected:
  ✅ Main Nameday and Disabled NOT saved to config
  ✅ On reopen: these columns auto-fitted (not custom size)
  ✅ Only 5 columns in config: Name, Other Nameday, Recipient, Email, Comment
Verification:
  1. Check config.json: only 5 columns in column_widths
  2. Reopen dialog: Main Nameday and Disabled are auto-fitted size
```

---

## 7. Integration Points

### Files Affected
1. **`app/managers/settings_manager.py`**
   - Add 2 new methods for dialog config

2. **`app/ui/database_editor_dialog.py`**
   - Update `__init()__` - load config
   - Update `_setup_ui()` - apply loaded widths
   - Add `_load_dialog_config()` method
   - Add `_apply_loaded_column_widths()` method
   - Update `closeEvent()` - save window size

### Backward Compatibility
- ✅ Existing `save_column_widths()` method unchanged
- ✅ Existing `_auto_fit_columns()` logic unchanged
- ✅ New code gracefully handles missing config (defaults to 900x600)
- ✅ Config structure extended (not breaking change)

### Dependencies
- `settings_manager` must be passed to `DatabaseEditorDialog` (already done)
- `logger` already imported in database_editor_dialog.py
- No new external dependencies

---

## 8. Code References

### Current State Locations
- Settings manager: `app/managers/settings_manager.py` (lines 1-125)
- Database editor dialog: `app/ui/database_editor_dialog.py` (lines 1-456)
- Config.json: `config/config.json`

### Existing Methods to Reference
- `save_column_widths()` in settings_manager (REQ-0059 reference implementation)
- `_auto_fit_columns()` in database_editor_dialog (REQ-0057 reference implementation)
- `closeEvent()` in database_editor_dialog (existing save logic location)

---

## 9. Success Criteria

✅ **Implementation Complete When:**
1. Dialog size persists to config.json on close
2. Dialog size restored from config on open
3. Column widths loaded from config skip auto-fit calculation
4. Invalid config triggers fallback (900x600 + auto-fit)
5. Only 5 column widths saved (3 auto-fit columns ignored)
6. All scenarios (1-6) pass testing
7. Logging provides clear visibility into config loading
8. No errors thrown on missing/invalid config
9. Column width and dialog size saved independently (can have one without other)

---

## 10. Notes & Caveats

### Important Implementation Details
1. **Window Position:** Deliberately not saved/restored to avoid multi-monitor issues
2. **Maximized State:** Not included; deferred to future release
3. **Auto-Fit Logic:** Only applies when config widths are missing or invalid
4. **Bounds Checking:** Dialog size must be 0 < size < 10000 (prevents absurd configs)
5. **Column Index Mapping:** Maintain consistent column index →name mapping (columns 0-7)

### Potential Edge Cases
- What if user resizes dialog to 40x40 (too small)? → Save it anyway; OS will enforce minimum
- What if column width becomes 0 during session? → Save it as-is; next open will trigger auto-fit (validation)
- What if config.json is read-only? → Log error, continue with defaults (non-blocking)
- What if settings_manager is None? → Dialog already requires it; would fail earlier

### Performance Considerations
- Skipping auto-fit when config exists reduces initialization time
- Auto-fit calculation only runs once per session (on open or on config miss)
- File I/O on close is synchronous (acceptable for single dialog close)

---

**Document End**  
**Next Step:** Proceed to Phase 1 implementation with SettingsManager updates.
