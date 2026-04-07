# REQ-0066 Implementation Plan: Reload Namedays Database

**Document ID:** 006_impl_add_db_reload_to_tray.md  
**Requirement:** REQ-0066 - Reload Namedays Database  
**Priority:** High  
**Created:** 2026-04-07

---

## 1. Requirement Overview

### Requirement Statement
System tray menu provides command to reload the namedays reference database from file without requiring application restart.

### Acceptance Criteria
- Menu option "Reload Namedays Database" available in tray context menu
- Clicking reloads namedays.csv without restarting application
- Notification shows confirmation of successful reload
- Handles file read errors gracefully with user feedback

### Dependencies
- REQ-0010: System Tray Icon
- REQ-0023: Nameday Date Format

### User Value
Allows users to update the namedays reference database (resources/namedays.csv) on-the-fly during application runtime without needing to restart the entire application.

---

## 2. Current State Analysis

### Existing System Components

#### 2.1 System Tray Icon [app/ui/system_tray.py]
- Class: `SystemTrayIcon(QSystemTrayIcon)`
- Current menu items:
  - Settings
  - Database
  - Query
  - Today's Namedays
  - Exit
- No reload/refresh functionality currently exists

#### 2.2 Nameday Reference Manager [app/managers/nameday_reference_manager.py]
- Class: `NamedayReferenceManager`
- Current functionality:
  - Loads namedays.csv on initialization
  - Provides methods to query namedays by name
  - Data stored in memory after load

#### 2.3 Application Architecture
- Main app: `NameDaysMonitoringApp` extends `QApplication`
- Monitoring engine runs in background thread
- Managers are initialized in `_setup_managers()`

### Current Limitations
1. Namedays database loaded once at application startup
2. Any changes to resources/namedays.csv require full application restart
3. No way to refresh reference database in-memory
4. No user notification mechanism for reload success/failure

---

## 3. Architecture Design

### 3.1 Component Modifications

```
NameDaysMonitoringApp (main.py)
    ↓
    ├─ nameday_ref: NamedayReferenceManager
    ↓
SystemTrayIcon (ui/system_tray.py)
    ↓
    └─ new signal: reload_namedays()
         ↓
      NamedayReferenceManager.reload() [NEW METHOD]
         ↓
      Notification to user
```

### 3.2 Data Flow During Reload

1. User clicks "Reload Namedays Database" menu item
2. Signal emitted: `reload_namedays()`
3. Manager.reload() called
4. CSV file re-read from disk
5. In-memory references refreshed
6. Success/error notification displayed to user
7. Cache invalidated (monitoring engine refreshes on next cycle)

---

## 4. Implementation Steps

### Step 1: Add Reload Method to NamedayReferenceManager

**File:** `app/managers/nameday_reference_manager.py`

**Task:** Add public `reload()` method that:
- Re-reads namedays.csv from disk
- Clears existing in-memory data
- Re-parses CSV file
- Returns success/error status

**Signature:**
```python
def reload(self) -> tuple[bool, str]:
    """
    Reload nameday reference database from file.
    
    Returns:
        tuple: (success: bool, message: str)
            - (True, "Reloaded X namedays") on success
            - (False, error_message) on failure
    """
```

**Implementation Details:**
- Catch FileNotFoundError → "Namedays file not found"
- Catch CSV parsing errors → "Invalid CSV format in namedays.csv"
- Catch encoding errors → "File encoding error"
- Return count of loaded records on success

### Step 2: Add Menu Item to System Tray

**File:** `app/ui/system_tray.py`

**Task:** Modify `_setup_menu()` to add new menu item

**Changes:**
```python
def _setup_menu(self):
    # ... existing menu items ...
    
    # Separator before reload option
    self.menu.addSeparator()
    
    # Reload Namedays Database action
    reload_action = self.menu.addAction(
        self._load_icon("reload.png"),  # or use text-only
        QCoreApplication.translate("SystemTrayIcon", 
                                   "Reload Namedays Database")
    )
    reload_action.triggered.connect(self._on_reload_namedays)
    
    # Separator before exit
    self.menu.addSeparator()
    
    # ... exit action ...
```

### Step 3: Add Handler Method to SystemTrayIcon

**File:** `app/ui/system_tray.py`

**Task:** Implement `_on_reload_namedays()` handler

**Implementation:**
```python
def _on_reload_namedays(self):
    """Handle Reload Namedays Database menu action."""
    logger.info("Reload Namedays Database action triggered")
    
    try:
        success, message = self.nameday_ref.reload()
        
        if success:
            # Success notification
            self.show_message(
                self.tr("Database Reloaded"),
                message,
                duration=3000
            )
            logger.info(f"Namedays database reloaded: {message}")
        else:
            # Error notification
            self.show_message(
                self.tr("Reload Failed"),
                message,
                duration=5000
            )
            logger.error(f"Failed to reload namedays: {message}")
            
    except Exception as e:
        logger.error(f"Unexpected error reloading namedays: {e}")
        self.show_message(
            self.tr("Reload Failed"),
            self.tr("Unexpected error: ") + str(e),
            duration=5000
        )
```

### Step 4: Add Translations

**File:** `app/i18n/app_hu.ts`

**New Translations Required:**
```xml
<context>
    <name>SystemTrayIcon</name>
    <message>
        <source>Reload Namedays Database</source>
        <translation>Névnapok adatbázisának újratöltése</translation>
    </message>
    <message>
        <source>Database Reloaded</source>
        <translation>Adatbázis újratöltve</translation>
    </message>
    <message>
        <source>Reload Failed</source>
        <translation>Újratöltés sikertelen</translation>
    </message>
    <message>
        <source>Unexpected error: </source>
        <translation>Váratlan hiba: </translation>
    </message>
</context>
```

### Step 5: Update Requirement Status

**File:** `Docs/requirements.md`

Once implemented, update REQ-0066 status from "proposed" to "implemented".

---

## 5. Detailed Code Changes

### 5.1 NamedayReferenceManager.reload()

**Location:** `app/managers/nameday_reference_manager.py`

```python
def reload(self) -> tuple[bool, str]:
    """
    Reload nameday reference database from file.
    
    Clears existing in-memory data and re-reads namedays.csv.
    
    Returns:
        tuple: (success: bool, message: str)
            - (True, "Reloaded N namedays") on success
            - (False, error_description) on failure
    
    Error Handling:
        - FileNotFoundError: "Namedays file not found"
        - ValueError/CSV errors: "Invalid CSV format"
        - UnicodeDecodeError: "File encoding error"
        - Any other exception: Generic error message
    """
    try:
        # Clear existing data
        self._namedays = {}
        self._nameday_count = 0
        
        # Re-load from file
        self._load_namedays_from_csv()
        
        # Return success with record count
        return (True, f"Reloaded {self._nameday_count} namedays")
        
    except FileNotFoundError:
        return (False, "Namedays file not found")
    except UnicodeDecodeError:
        return (False, "File encoding error - ensure UTF-8 encoding")
    except ValueError as e:
        return (False, f"Invalid CSV format: {str(e)}")
    except Exception as e:
        return (False, f"Error loading file: {str(e)}")
```

### 5.2 SystemTrayIcon._setup_menu()

**Location:** `app/ui/system_tray.py`

Add between "Today's Namedays" and separator before "Exit":

```python
# Within _setup_menu() method

# ... existing menu items ...

today_action = self.menu.addAction(
    self._load_icon("today.png"), 
    self.tr("Today's Namedays")
)
today_action.triggered.connect(self._on_today)

# NEW: Separator before reload
self.menu.addSeparator()

# NEW: Reload Namedays Database action
reload_action = self.menu.addAction(
    self.tr("Reload Namedays Database")
)
reload_action.triggered.connect(self._on_reload_namedays)

# Existing separator
self.menu.addSeparator()

# Exit action
exit_action = self.menu.addAction(
    self._load_icon("exit.png"), 
    QCoreApplication.translate("SystemTrayIcon", "Exit")
)

logger.info("System tray menu setup complete with actions: Settings, Database, Query, Today's Namedays, Reload Namedays Database, Exit")
```

### 5.3 SystemTrayIcon._on_reload_namedays()

**Location:** `app/ui/system_tray.py`

Add new method to `SystemTrayIcon` class:

```python
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
```

---

## 6. Testing Strategy

### 6.1 Unit Tests

**Test File:** `tests/test_nameday_reference_manager.py`

```python
def test_reload_valid_csv():
    """Test reload with valid CSV file."""
    manager = NamedayReferenceManager(NAMEDAYS_CSV_PATH)
    success, message = manager.reload()
    assert success is True
    assert "Reloaded" in message

def test_reload_missing_file():
    """Test reload with missing file."""
    manager = NamedayReferenceManager("/nonexistent/path.csv")
    success, message = manager.reload()
    assert success is False
    assert "not found" in message.lower()

def test_reload_invalid_encoding():
    """Test reload with invalid encoding."""
    # Create temporary file with invalid encoding
    # Assert proper error message returned
    pass
```

### 6.2 Integration Tests

1. **Verify menu item appears** in tray context menu
2. **Verify click triggers reload** without crashing
3. **Verify success notification appears** with correct message
4. **Verify error notification appears** when file missing
5. **Verify database still works** after reload (query functionality)

### 6.3 Manual Testing

1. Launch application
2. Right-click system tray icon
3. Verify "Reload Namedays Database" visible in menu
4. Click menu item
5. Verify notification appears (success or error)
6. Edit resources/namedays.csv (add/remove entry)
7. Click reload again
8. Verify new data is reflected in Query dialog

---

## 7. Acceptance Criteria Checklist

| Criterion | Status | Notes |
|-----------|--------|-------|
| Menu option visible in tray context menu | ✓ Planned | Added in _setup_menu() |
| Menu option has clear label | ✓ Planned | "Reload Namedays Database" |
| Clicking option reloads CSV without restart | ✓ Planned | reload() method implementation |
| Success notification displayed | ✓ Planned | show_message() with record count |
| File read errors handled gracefully | ✓ Planned | Try/except with user-friendly messages |
| Error notification displayed | ✓ Planned | show_message() with error details |
| Translations provided (Hungarian) | ✓ Planned | 4 new translation strings |
| Logging added for audit trail | ✓ Planned | logger.info/error calls |
| No disruption to other functionality | Pending | Integration testing required |

---

## 8. File Modifications Summary

| File | Changes | Scope |
|------|---------|-------|
| `app/managers/nameday_reference_manager.py` | Add `reload()` method (12-15 lines) | New public method |
| `app/ui/system_tray.py` | Add menu item, handler method (~25 lines) | Menu UI + Handler |
| `app/i18n/app_hu.ts` | Add 4 translation strings | Localization |
| `Docs/requirements.md` | Update REQ-0066 status | Documentation |

---

## 9. Dependencies and Prerequisites

### Required Libraries
- All existing (PyQt5, csv module, logging)
- No new dependencies

### File Access
- `resources/namedays.csv` must be readable
- Error handling for file permission issues

### Thread Safety
- Manager reload() is synchronous
- Called from main GUI thread (menu click handler)
- No threading concerns for this implementation

---

## 10. Risk Analysis

### Low Risk Areas
✓ Menu item addition (isolated UI change)  
✓ Manager reload method (local file I/O)  
✓ Error handling (defensive coding)

### Potential Issues
- File permissions: CSV file might not be readable
  - Mitigation: Clear error message to user
- Large CSV files: Reload might briefly freeze UI
  - Mitigation: Currently acceptable; could add threading if needed
- Concurrent access: Other code might access manager during reload
  - Mitigation: Known limitation; add documentation

### Mitigation Strategies
1. **Comprehensive error handling** with user-friendly messages
2. **Logging at INFO level** for reload events
3. **Defensive programming** in manager reload logic
4. **User notification** ensures visibility of success/failure

---

## 11. Future Enhancements

Potential follow-up improvements:
- Add icon for menu item (reload/refresh icon)
- Implement async reload for large files (threading)
- Monitor file change events for automatic reload
- Add reload shortcut key
- Statistics: "Reloaded 247 namedays from 14 countries"

---

## 12. Rollback Plan

If issues occur:
1. Remove menu item from _setup_menu()
2. Comment out handler method
3. Feature gracefully unavailable but no crashes
4. No data loss (read-only operation)

---

## 13. Implementation Checklist

- [ ] Add `reload()` method to NamedayReferenceManager
- [ ] Add menu item to SystemTrayIcon._setup_menu()
- [ ] Implement `_on_reload_namedays()` handler
- [ ] Add Hungarian translations to app_hu.ts
- [ ] Write and run unit tests
- [ ] Manual testing with valid/invalid CSV files
- [ ] Verify menu item positioning and appearance
- [ ] Test error scenarios (missing file, bad encoding)
- [ ] Test notification display (success and error)
- [ ] Update documentation
- [ ] Code review and testing sign-off

---

**Implementation Status:** Ready for development  
**Estimated Effort:** 2-3 hours (including testing)  
**Complexity:** Low to Medium
