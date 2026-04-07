# Implementation Plan: Monitoring Cache Invalidation on Contact Changes

**Document ID:** 005_impl_monitoring_cache_invalidation.md  
**Created:** April 2, 2026  
**Status:** Ready for Implementation  
**Owner:** Development Team

---

## 1. Overview

**Objective:** Invalidate monitoring engine's daily check cache when contacts are added/modified, ensuring newly added contacts with today's nameday are detected

**Requirement:** REQ-0065 - Monitoring Cache Invalidation on Contact Changes

**Problem Statement:**
When a user adds a new contact with today's nameday AFTER the first morning monitoring check, the contact is NOT detected because the monitoring engine has already checked today's date and skipped subsequent checks. This prevents real-time notification generation for newly added contacts.

**Root Cause:**
The `MonitoringEngine.check_namedays()` method caches the last check date (`_last_check_date`) to prevent duplicate database queries. Once set to today's date, subsequent calls on the same day return early without re-scanning the contact database:

```python
if self._last_check_date == today_date:
    return []  # Early return - misses newly added contacts!
```

**Solution:**
Provide a method `invalidate_check_cache()` in MonitoringEngine to reset the cache. Call this from AddEditContactDialog when a contact is saved, forcing the next monitoring cycle to perform a fresh database check.

---

## 2. Requirements Summary

| Requirement | Details |
|---|---|
| **ID** | REQ-0065 |
| **Title** | Monitoring Cache Invalidation on Contact Changes |
| **Priority** | High |
| **Description** | Monitoring engine invalidates its daily check cache when contacts are added or modified, ensuring newly added contacts with today's nameday are detected on next monitoring cycle |
| **Acceptance Criteria** | When contact added/modified via AddEditContactDialog, monitoring cache invalidated; next monitoring cycle performs fresh check; newly added contacts with today's nameday generate notifications (within next interval) |
| **Dependencies** | REQ-0022 (Background Monitoring), REQ-0011 (Edit Database), REQ-0004 (Multiple Names Same Day) |

---

## 3. Architecture & Design

### Current Behavior (Problem)
```
Timeline:
08:00:00 - App starts → Monitoring checks at startup
08:00:05 - First check complete → _last_check_date = "04-02"
08:30:00 - User adds new contact "János" (celebrates today)
08:31:00 - Monitoring cycle runs → checks _last_check_date == "04-02" → returns early ❌
08:32:00 - Monitoring cycle runs → same result ❌
...
No notification generated for newly added contact!
```

### Fixed Behavior (Solution)
```
Timeline:
08:00:00 - App starts → Monitoring checks at startup
08:00:05 - First check complete → _last_check_date = "04-02"
08:30:00 - User adds new contact "János" (celebrates today)
08:30:15 - AddEditContactDialog calls invalidate_check_cache()
08:30:15 - _last_check_date reset to None
08:31:00 - Monitoring cycle runs → _last_check_date is None → performs fresh check ✅
08:31:02 - Finds "János" in database → generates notification ✅
08:31:05 - Notification displayed to user ✅
```

### Design Decision
- **Location:** MonitoringEngine method + AddEditContactDialog integration call
- **Pattern:** Cache invalidation on data mutation
- **Thread-safe:** Simple None assignment is atomic in Python
- **Benefit:** Minimal code change, immediate detection, no performance impact

### Diagram
```
Contact Saved/Modified Flow:
┌─────────────────────────────────────┐
│ User saves/creates contact          │
│ in AddEditContactDialog              │
└────────────────────┬────────────────┘
                     │
                     ▼
┌─────────────────────────────────────┐
│ Dialog saves to CSV via manager      │
└────────────────────┬────────────────┘
                     │
                     ▼
┌─────────────────────────────────────┐
│ Dialog calls:                        │
│ monitoring_engine.invalidate_cache() │
└────────────────────┬────────────────┘
                     │
                     ▼
┌─────────────────────────────────────┐
│ MonitoringEngine._last_check_date    │
│ set to None                          │
└────────────────────┬────────────────┘
                     │
        ┌────────────▼────────────┐
        │                         │
        ▼                         ▼
   Next Cycle 1s          Next Cycle 60s
   (early, fresh)         (if earlier missed)
        │                         │
        ▼                         ▼
  Fresh check        Fresh check of DB
  of database        New contact detected!
  New contact          Notification ✅
  detected! ✅
```

---

## 4. Implementation

### Files to Modify
1. **app/core/monitoring_engine.py** - Add cache invalidation method
2. **app/ui/add_edit_contact_dialog.py** - Call invalidation on save

### Changes

#### File 1: app/core/monitoring_engine.py (Add New Method)

**Location:** After `set_interval()` method (around line 160)

**New Method to Add:**
```python
def invalidate_check_cache(self) -> None:
    """
    Invalidate daily check cache to force fresh check on next cycle [REQ-0065].
    
    Called when contacts are added/modified to ensure newly added contacts
    with today's nameday are detected on next monitoring cycle.
    
    This is a no-op if monitoring is not running, but safe to call anytime.
    """
    if self._last_check_date is not None:
        logger.info(f"Invalidating check cache (was: {self._last_check_date}) [REQ-0065]")
        self._last_check_date = None
    else:
        logger.debug("Check cache already invalidated [REQ-0065]")
```

#### File 2: app/ui/add_edit_contact_dialog.py (Call Invalidation)

**Location:** In `_validate_and_save()` method, after successful CRUD operation

**Current Code (Around Line 200-220):**
```python
def _validate_and_save(self):
    """Three-layer validation and save."""
    # Layer 1: UI validation
    errors = self._validate_fields()
    if errors:
        QMessageBox.warning(self, "Validation Error", "\n".join(errors))
        return
    
    # Layer 2: Build contact object
    contact = self._build_contact_from_form()
    
    # Layer 3: Validate and persist
    try:
        self._persist_contact(contact)
        QMessageBox.information(self, "Success", "Contact saved successfully!")
        self.accept()
    except Exception as e:
        logger.error(f"Error saving contact: {e}")
        QMessageBox.critical(self, "Error", f"Failed to save contact: {e}")
```

**Modified Code (Add cache invalidation call):**
```python
def _validate_and_save(self):
    """Three-layer validation and save."""
    # Layer 1: UI validation
    errors = self._validate_fields()
    if errors:
        QMessageBox.warning(self, "Validation Error", "\n".join(errors))
        return
    
    # Layer 2: Build contact object
    contact = self._build_contact_from_form()
    
    # Layer 3: Validate and persist
    try:
        self._persist_contact(contact)
        
        # Invalidate monitoring cache so newly added contacts are detected [REQ-0065]
        # This ensures next monitoring cycle performs fresh check of updated database
        from app.main import NameDaysMonitoringApp
        app = NameDaysMonitoringApp.instance()
        if app and hasattr(app, 'monitoring_engine'):
            app.monitoring_engine.invalidate_check_cache()
            logger.info("Monitoring cache invalidated after contact save [REQ-0065]")
        
        QMessageBox.information(self, "Success", "Contact saved successfully!")
        self.accept()
    except Exception as e:
        logger.error(f"Error saving contact: {e}")
        QMessageBox.critical(self, "Error", f"Failed to save contact: {e}")
```

**Explanation of Changes:**
1. After successful `_persist_contact()` call, get reference to the running app
2. Check that monitoring_engine exists (it should, but we're defensive)
3. Call `invalidate_check_cache()` to force fresh database check on next cycle
4. Log the action for audit trail

---

## 5. Implementation Checklist

- [ ] Add `invalidate_check_cache()` method to MonitoringEngine (app/core/monitoring_engine.py)
- [ ] Update method to set `_last_check_date = None`
- [ ] Add logging for cache invalidation
- [ ] Update `_validate_and_save()` in AddEditContactDialog to import app instance
- [ ] Add call to `app.monitoring_engine.invalidate_check_cache()` after successful save
- [ ] Add error handling for missing app instance (defensive programming)
- [ ] Verify: 0 syntax errors in both files
- [ ] Test: Scenario 1 - Add contact with today's nameday
- [ ] Test: Scenario 2 - Edit existing contact to today's nameday
- [ ] Test: Scenario 3 - Verify log shows cache invalidation
- [ ] Test: Scenario 4 - Verify fresh check happens within 1 minute
- [ ] Verify: Both ADD and EDIT modes trigger invalidation
- [ ] Document fix in session notes

---

## 6. Testing Scenarios

### Scenario 1: Add New Contact with Today's Nameday (Manual Testing)
```
Pre-condition: App running with monitoring active (1-minute interval)
Steps:
  1. Note current time (e.g., 14:30:00)
  2. Wait ~10 seconds for monitoring to run (first cycle after startup)
  3. Observe in logs: "Performing full nameday check" or "Already checked today"
  4. Open "Edit Notification Database"
  5. Click "Add Contact"
  6. Enter: Name="János", Main Nameday="04-02" (today), Recipient="Test"
  7. Click "Add Email" → enter "test@example.com"
  8. Click "Save"
Expected:
  ✅ Dialog shows "Contact saved successfully"
  ✅ Log shows: "Invalidating check cache (was: 04-02) [REQ-0065]"
  ✅ Log shows: "Monitoring cache invalidated after contact save [REQ-0065]"
  ✅ Within 30 seconds, monitoring log shows: "Performing full nameday check for 04-02 [REQ-0022]"
  ✅ Followed by: "Found nameday: János on 04-02"
  ✅ Notification queued and displayed for "János"
Verification:
  - New contact NOT missed by monitoring
  - Notification appears within same monitoring cycle
```

### Scenario 2: Edit Existing Contact to Change Nameday to Today
```
Pre-condition: Contact "Maria" with nameday "06-24" exists; app running
Steps:
  1. Wait for monitoring cycle to complete (verify logs)
  2. Open "Edit Notification Database"
  3. Find "Maria" contact, click "Edit"
  4. Change Main Nameday from "06-24" to "04-02" (today)
  5. Click "Save"
Expected:
  ✅ Log shows: "Invalidating check cache (was: 04-02) [REQ-0065]"
  ✅ Within 30 seconds: "Performing full nameday check" (forced by invalidation)
  ✅ "Found nameday: Maria on 04-02"
Verification:
  - Contact change immediately detected by monitoring
```

### Scenario 3: Cache Invalidation Appears in Logs
```
Pre-condition: App running, monitoring active
Steps:
  1. Add new contact via dialog (as in Scenario 1)
  2. Check application logs (in logs/ directory)
Expected:
  ✅ Log entry: "[INFO] Invalidating check cache (was: 04-02) [REQ-0065]"
  ✅ Log entry: "[INFO] Monitoring cache invalidated after contact save [REQ-0065]"
  ✅ Log entry: "[INFO] Performing full nameday check for 04-02 [REQ-0022]"
Verification:
  - Sequence shows invalidation → fresh check
  - Timestamps very close together
```

### Scenario 4: Fresh Check Happens Within 1 Minute
```
Pre-condition: App running with 1-minute monitoring interval
Steps:
  1. Add contact at 14:30:45
  2. Watch logs for next 60 seconds
Expected:
  ✅ Cache invalidated at 14:30:45
  ✅ Next monitoring cycle (usually within 5-30 seconds) shows "Performing full nameday check"
  ✅ Fresh check detects new contact
  ✅ Notification generated within 60 seconds (typically within 10-30 seconds)
Verification:
  - User doesn't need to wait full interval for notification
  - Fast detection for same-day additions
```

### Scenario 5: Multiple Contacts Added in Succession
```
Pre-condition: App running with monitoring active
Steps:
  1. Add contact "János" with today's nameday
  2. Wait 5 seconds (before next monitoring cycle)
  3. Add contact "Mihály" with today's nameday
  4. Watch for both notifications
Expected:
  ✅ Both contacts detected by next monitoring cycle
  ✅ Both generate notifications
  ✅ Log shows two invalidations and fresh check catching both
Verification:
  - Multiple additions handled correctly
  - No race conditions
```

### Scenario 6: Editing Non-Matching Contact Doesn't Affect Other Notifications
```
Pre-condition: Contact "János" with today's nameday already notified
Steps:
  1. Edit different contact "Maria" (change comment field only, not nameday)
  2. Observe monitoring behavior
Expected:
  ✅ Cache invalidated for "Maria" edit
  ✅ Fresh check still finds "János" (no duplicate re-notification)
  ✅ Notification handling respects deduplication
Verification:
  - Cache invalidation doesn't break existing deduplication logic
```

---

## 7. Integration Points

### Files Affected
1. **app/core/monitoring_engine.py** (1 new method)
2. **app/ui/add_edit_contact_dialog.py** (1 method modification)

### Dependencies
- **Internal:** NameDaysMonitoringApp instance (via QApplication.instance())
- **External:** None (no new imports needed in monitoring_engine.py)

### Call Chain
```
User clicks "Save" in AddEditContactDialog
  ↓
_persist_contact(contact) succeeds
  ↓
Get app instance via NameDaysMonitoringApp.instance()
  ↓
Call app.monitoring_engine.invalidate_check_cache()
  ↓
Set _last_check_date = None
  ↓
Log action
  ↓
Next monitoring cycle (within 60 seconds)
  ↓
Fresh database check because _last_check_date is None
  ↓
New contacts detected and notifications generated
```

### Backward Compatibility
- ✅ No breaking changes
- ✅ Existing monitoring functionality preserved
- ✅ Optimization (cache) still works for non-contact-change scenarios
- ✅ Only adds detection capability for newly added contacts
- ✅ All existing code using AddEditContactDialog works unchanged

### No Impact On
- ContactDatabaseManager
- NotificationManager
- NotificationQueue
- EmailService
- Settings persistence
- UI dialogs (except AddEditContactDialog)

---

## 8. Quick Reference

### What Gets Called When User Saves Contact
```
AddEditContactDialog._validate_and_save()
  ↓
  contact = self._build_contact_from_form()
  ↓
  self._persist_contact(contact)  # Saves to CSV
  ↓
  app = NameDaysMonitoringApp.instance()
  ↓
  app.monitoring_engine.invalidate_check_cache()  ← NEW
  ↓
  self.accept()  # Close dialog
```

### Before Fix
```python
# In MonitoringEngine.check_namedays():
if self._last_check_date == today_date:
    return []  # ← Prevents detection of new contacts added after first check
```

### After Fix
```python
# In MonitoringEngine.check_namedays():
if self._last_check_date == today_date:
    return []

# NEW METHOD:
def invalidate_check_cache(self):
    self._last_check_date = None  # ← Force next check to be fresh
```

---

## 9. Success Criteria

✅ **Implementation Complete When:**
1. `invalidate_check_cache()` method added to MonitoringEngine
2. Method sets `_last_check_date = None`
3. Method includes proper logging
4. AddEditContactDialog calls invalidation after successful save
5. App instance retrieved safely with defensive checks
6. No syntax errors in either file
7. Both ADD and EDIT operations call invalidation
8. All 6 test scenarios pass
9. Log shows cache invalidation followed by fresh check
10. Newly added contacts detected within 1 monitoring cycle (~60 seconds)

---

## 10. Execution Notes

**Required Actions:**
1. Add `invalidate_check_cache()` to MonitoringEngine (3-4 lines)
2. Import app instance in AddEditContactDialog
3. Call invalidation after `_persist_contact()` succeeds (2-3 lines)
4. Add error handling for missing app instance
5. Run syntax check: `get_errors(['app/core/monitoring_engine.py', 'app/ui/add_edit_contact_dialog.py'])`
6. Execute test scenarios 1-6
7. Verify log output contains REQ-0065 and REQ-0022 entries

**Estimated Time:** 5-10 minutes

**Risk Level:** Very Low
- Minimal code change (total ~10 lines added)
- No complex logic, just one setter call
- No external dependencies
- Defensive programming (check for app instance)
- Non-intrusive (only adds invalidation, doesn't change check logic)

**Rollback:** If needed, simply remove the invalidation call from AddEditContactDialog and the new method from MonitoringEngine.

**Thread Safety:** The assignment `_last_check_date = None` is atomic in Python (single bytecode operation), so no lock needed. Worst case: one unnecessary fresh check.

---

**Document End**  
**Next Step:** Implement the fix in monitoring_engine.py and add_edit_contact_dialog.py, then verify against test scenarios.
