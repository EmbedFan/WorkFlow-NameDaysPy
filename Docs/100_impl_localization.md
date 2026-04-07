# Implementation Plan: Application Localization (REQ-0045, REQ-0046)

**Document ID:** 100_impl_localization.md  
**Status:** Implementation Ready  
**Requirements:** REQ-0045 (Language Selection), REQ-0046 (Multilingual UI Support)  
**Dependencies:** PyQt5 (already installed)  
**Effort:** ~2-3 hours (most time spent on translation, code changes are minimal)

---

## Overview

This document guides implementation of Hungarian localization for the Name Days application. The feature enables users to switch between English and Hungarian UI languages with persistence across application restarts.

### Architecture

```
User selects language in Settings
        ↓
Language saved to config.json
        ↓
On app restart: Load translator for selected language
        ↓
Install QTranslator to application
        ↓
All .tr() wrapped strings display in selected language
```

### Translation Workflow

```
1. Extract UI strings → app/i18n/app_en.ts
2. Create Hungarian file → app/i18n/app_hu.ts (copy of app_en.ts)
3. Translate strings → app_hu.ts (manual, ~34 strings)
4. Compile → app/i18n/app_hu.qm (binary format)
5. Load translator → install_translator() in main.py
6. Test in app → Switch language in Settings
```

---

## Phase 1: Code Structure (2 hours estimated)

### Files to Create

#### 1. app/i18n/translator.py

**Purpose:** Translation/localization manager module  
**Size:** ~80 lines  
**Dependencies:** PyQt5.QtCore (QTranslator, QCoreApplication), app.utils.logger

**Full Implementation:**

```python
"""
Translation/Localization manager [REQ-0045, REQ-0046].

Handles loading and switching between language translations.
"""

from pathlib import Path
from PyQt5.QtCore import QTranslator, QCoreApplication
from app.utils import get_logger

logger = get_logger(__name__)

TRANSLATIONS_DIR = Path(__file__).parent
TRANSLATION_FILES = {
    "en": "app_en",
    "hu": "app_hu"
}


def load_translator(language: str = "en") -> QTranslator:
    """
    Load and install translator for specified language [REQ-0046].
    
    Args:
        language: Language code ("en" or "hu")
    
    Returns:
        Loaded QTranslator instance
    
    Raises:
        FileNotFoundError: If translation file (.qm) not found
    """
    # Get translation filename
    ts_filename = TRANSLATION_FILES.get(language, "app_en")
    qm_path = TRANSLATIONS_DIR / f"{ts_filename}.qm"
    
    # Check if file exists
    if not qm_path.exists():
        logger.warning(f"Translation file not found: {qm_path}")
        logger.info(f"Using default language (English)")
        return QTranslator()  # Return empty translator (falls back to English)
    
    # Load translator
    translator = QTranslator()
    if translator.load(str(qm_path)):
        logger.info(f"Loaded translation: {language} from {qm_path}")
        return translator
    else:
        logger.error(f"Failed to load translation: {language}")
        return QTranslator()


def install_translator(app: QCoreApplication, language: str = "en") -> None:
    """
    Install translator to application [REQ-0046].
    
    Args:
        app: QApplication instance
        language: Language code ("en" or "hu")
    """
    translator = load_translator(language)
    app.installTranslator(translator)
    logger.info(f"Translator installed: {language} [REQ-0046]")


def switch_language(app: QCoreApplication, language: str) -> None:
    """
    Switch application language at runtime [REQ-0045].
    
    Uninstalls old translator and installs new one for specified language.
    
    Args:
        app: QApplication instance
        language: Language code ("en" or "hu")
    """
    # Remove old translators
    for translator in app.findChildren(QTranslator):
        app.removeTranslator(translator)
    
    # Install new translator
    install_translator(app, language)
    logger.info(f"Language switched to: {language}")
```

**Checklist:**
- [ ] Create file at `app/i18n/translator.py`
- [ ] Copy code exactly as shown above
- [ ] Verify no syntax errors (IDE should show green checkmark)

---

### Files to Modify

#### 2. app/main.py

**Location:** In `NameDaysMonitoringApp.__init__()` method, after managers are initialized

**Find Section:** Look for where managers are set up (around line 70, search for `self.settings_manager = SettingsManager()`)

**Modification A: Add import at top of file**

```python
# Add this line with other imports at the top
from app.i18n.translator import install_translator
```

**Location tip:** Look for other `from app.` imports near top of file and add after them.

**Modification B: Add translator initialization after manager setup**

**Find this code:**
```python
# Managers
self.settings_manager = SettingsManager()
self.contact_db_manager = ContactDatabaseManager()
self.nameday_manager = NamedayReferenceManager()
```

**Add after it (before notification_manager setup):**
```python
        # Managers
        self.settings_manager = SettingsManager()
        self.contact_db_manager = ContactDatabaseManager()
        self.nameday_manager = NamedayReferenceManager()
        
        # Load appropriate language translator [REQ-0046]
        user_language = self.settings_manager.language  # "en" or "hu"
        install_translator(self, user_language)
        self.logger.info(f"Language set to: {user_language} [REQ-0046]")
        
        # Notification Manager
        self.notification_manager = NotificationManager(...)
```

**Checklist:**
- [ ] Add import: `from app.i18n.translator import install_translator`
- [ ] Find managers initialization section
- [ ] Add 3 lines: translator initialization + logging
- [ ] Verify indentation matches surrounding code
- [ ] No syntax errors

---

#### 3. app/ui/settings_dialog.py

**Location:** In the `accept()` method where settings are saved

**Find this method:**
```python
def accept(self):
    """Save settings and apply changes."""
    # ... existing code ...
```

**Add language switching logic after existing save code:**

```python
def accept(self):
    """Save settings and apply changes."""
    # ... existing save logic (don't modify) ...
    
    # If language changed, reload UI [REQ-0045]
    if hasattr(self, 'language_changed') and self.language_changed:
        from app.i18n.translator import switch_language
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtWidgets import QMessageBox
        
        new_language = self.language_combo.currentData()
        switch_language(QApplication.instance(), new_language)
        
        # Show message to user
        QMessageBox.information(
            self,
            self.tr("Language Changed"),
            self.tr("Language will be fully applied after application restart.")
        )
    
    # Call parent accept
    super().accept()
```

**Note:** This assumes `language_combo` exists in the dialog. If not, this code can be skipped for now and added later when language dropdown is fully implemented.

**Checklist:**
- [ ] Find `accept()` method in settings_dialog.py
- [ ] Add language switching code before `super().accept()`
- [ ] Verify imports are included
- [ ] No syntax errors

---

#### 4. app/managers/settings_manager.py

**Location:** In the `get_setting()` method or properties

**Modification:** Add language property validation

**Find code like:**
```python
def get_setting(self, key: str) -> Any:
    """Get specific setting by key."""
    # ... existing code ...
```

**Add language handling:**
```python
def get_setting(self, key: str) -> Any:
    """Get specific setting by key."""
    if key == "language":
        language = getattr(self._settings, "language", "en")
        # Validate against supported languages
        from app.constants import SUPPORTED_LANGUAGES
        if language not in SUPPORTED_LANGUAGES:
            language = "en"
        return language
    
    # ... rest of existing code ...
```

**Alternative:** If using property-based access, add language property:

```python
@property
def language(self) -> str:
    """Get user's preferred language."""
    language = getattr(self._settings, "language", "en")
    from app.constants import SUPPORTED_LANGUAGES
    if language not in SUPPORTED_LANGUAGES:
        language = "en"
    return language
```

**Checklist:**
- [ ] Find settings_manager.py
- [ ] Add language property or validation in get_setting()
- [ ] Verify SUPPORTED_LANGUAGES import works (should already exist in constants.py)
- [ ] No syntax errors

---

## Phase 2: Translation Files (30 minutes estimated)

### Files Created by Scripts

**These are auto-generated by running provided scripts - no manual creation needed.**

**After running `python extract_translations.py`:**
- ✅ Creates: `app/i18n/app_en.ts`

**After translating strings:**
- ✅ Edit: `app/i18n/app_hu.ts` (copy of app_en.ts with Hungarian translations)

**After running `python ts_to_qm.py`:**
- ✅ Creates: `app/i18n/app_hu.qm` (binary compiled format)
- ✅ Creates: `app/i18n/app_en.qm` (binary compiled format)

---

## Phase 3: Extract and Translate (1.5 hours estimated)

### Step 1: Extract English Strings

```bash
cd c:\Munka\2026\AiWorkFlows\WorkFlow-NameDaysPy
python extract_translations.py
```

**Expected output:**
```
Found 42 Python files
Extracting translatable strings...
✓ Successfully created: app\i18n\app_en.ts (34 messages)
```

**Checklist:**
- [ ] Run command in PowerShell
- [ ] Check that `app/i18n/app_en.ts` was created
- [ ] File size > 10KB

### Step 2: Create Hungarian Translation

**Copy English template:**
```bash
copy app\i18n\app_en.ts app\i18n\app_hu.ts
```

**Edit the file in VS Code:**
```
app\i18n\app_hu.ts
```

**Change language attribute:**
```xml
<!-- Change from: -->
<TS version="2.1">

<!-- To: -->
<TS version="2.1" language="hu_HU">
```

**Translate all `<translation>` tags** (34 strings to translate)

**Hungarian Translation Reference:**

| English | Hungarian | Context |
|---|---|---|
| Settings | Beállítások | Menu |
| Database | Adatbázis | Menu |
| Query | Keresés | Menu |
| Today's Namedays | Mai névnapok | Menu |
| Exit | Kilépés | Menu |
| Edit Contact | Kapcsolat szerkesztése | Dialog |
| Add New Contact | Új kapcsolat hozzáadása | Dialog |
| Contact Name * | Kapcsolat neve * | Form |
| Email Addresses | E-mail címek | Form |
| Save | Mentés | Button |
| Cancel | Mégse | Button |
| Close | Bezárás | Button |
| Delete | Törlés | Button |
| Contact Database | Kapcsolatok adatbázisa | Title |
| Name | Név | Table header |
| Email | E-mail | Table header |
| Recipient | Címzett | Table header |
| Comment | Megjegyzés | Table header |
| Disabled | Letiltva | Table header |

**Checklist:**
- [ ] Copy app_en.ts to app_hu.ts
- [ ] Change `<TS>` tag to include `language="hu_HU"`
- [ ] Find all `<translation type="unfinished">` or empty `<translation></translation>`
- [ ] Add Hungarian text to each translation tag
- [ ] Save file in UTF-8 encoding

### Step 3: Compile Translations

```bash
python ts_to_qm.py
```

**Expected output:**
```
Found 2 translation files:
  - app\i18n\app_en.ts
  - app\i18n\app_hu.ts

Compiling translations...

✓ Compiled: app/i18n/app_en.ts
  Messages: 34/34 translated
  Output: app\i18n\app_en.qm (5234 bytes)

✓ Compiled: app/i18n/app_hu.ts
  Messages: 34/34 translated
  Output: app\i18n\app_hu.qm (5234 bytes)

============================================================
✓ All translations compiled successfully!
```

**Checklist:**
- [ ] Run command in PowerShell
- [ ] Check both `.qm` files created
- [ ] File sizes > 1KB (not 4 bytes)
- [ ] Both show 34/34 messages translated

---

## Phase 4: Code Integration & Testing (30 minutes estimated)

### Step 1: Implement Code Changes

**In order:**
1. ✅ Create `app/i18n/translator.py` (Phase 1)
2. ✅ Modify `app/main.py` (Phase 1)
3. ✅ Modify `app/managers/settings_manager.py` (Phase 1)
4. ⏳ Modify `app/ui/settings_dialog.py` (Phase 1) - *Optional, can skip if language UI not fully implemented*

### Step 2: Verify No Syntax Errors

```bash
# Check for Python syntax errors
python -m py_compile app/i18n/translator.py
python -m py_compile app/main.py
python -m py_compile app/managers/settings_manager.py
```

**Expected:** No output = success

### Step 3: Run Application

```bash
python main.py
```

**Test Scenario 1: Default English**
- [ ] Application launches without errors
- [ ] All UI displays in English
- [ ] Settings dialog shows "English" selected
- [ ] No exceptions in console/logs

**Test Scenario 2: Switch to Hungarian**
- [ ] Open Settings dialog
- [ ] Look for language dropdown/selection
- [ ] Change to Hungarian
- [ ] Save/OK
- [ ] Check if strings appear in Hungarian
- [ ] Note: May require app restart for full effect

**Test Scenario 3: Persistence**
- [ ] Close application
- [ ] Restart application
- [ ] Verify language selected previously is still active

---

## Verification & Quality Assurance

### Code Quality Checks

**Checklist:**
- [ ] No Python syntax errors (run py_compile)
- [ ] No import errors (all imports resolve)
- [ ] Logger calls use correct format
- [ ] Indentation consistent (4 spaces)
- [ ] Type hints correct where used

### Functional Testing

**English Display:**
- [ ] Menu shows: Settings, Database, Query, Today's Namedays, Exit (in English)
- [ ] All dialogs titled in English
- [ ] All buttons labeled in English

**Hungarian Display:**
- [ ] Menu shows: Beállítások, Adatbázis, Keresés, Mai névnapok, Kilépés
- [ ] All dialogs titled in Hungarian
- [ ] All buttons labeled in Hungarian

**Language Persistence:**
- [ ] Setting language to Hungarian, restart app → Still Hungarian
- [ ] Setting language to English, restart app → Still English

### File Structure Verification

```
app/
├── i18n/
│   ├── __init__.py          (exists)
│   ├── translator.py        (NEW - created)
│   ├── app_en.ts           (NEW - created by extract)
│   ├── app_hu.ts           (NEW - created by translate)
│   ├── app_en.qm           (NEW - created by compile)
│   └── app_hu.qm           (NEW - created by compile)
├── main.py                  (MODIFIED - translator import + init)
├── managers/
│   └── settings_manager.py  (MODIFIED - language property)
└── ui/
    └── settings_dialog.py   (MODIFIED - language switching)
```

---

## Rollback/Undo Procedure

If implementation fails, rollback in this order:

1. **Delete translation files** (safe - can regenerate):
   ```bash
   del app\i18n\translator.py
   del app\i18n\app_en.ts
   del app\i18n\app_hu.ts
   del app\i18n\app_en.qm
   del app\i18n\app_hu.qm
   ```

2. **Revert code modifications** (use git or restore original files):
   - `app/main.py` - Remove translator import and initialization
   - `app/managers/settings_manager.py` - Remove language property
   - `app/ui/settings_dialog.py` - Remove language switching code

3. **Restart application** - Should work as before

---

## Estimated Timeline

```
Phase 1 (Code Structure):    2 hours
  - Create translator.py
  - Modify main.py
  - Modify settings_manager.py
  - Modify settings_dialog.py

Phase 2 (Translation Setup): 30 minutes
  - Run extract script
  - Copy/create Hungarian file
  - Set up file headers

Phase 3 (Translate):         1-1.5 hours
  - Translate 34 strings (~30 seconds each)
  - Run compile script

Phase 4 (Integration/Test):  30 minutes
  - Implement remaining code
  - Run tests
  - Verify functionality

TOTAL:                        ~4 hours
```

---

## Dependencies & Prerequisites

✅ **Already Available:**
- PyQt5 (main framework)
- app.utils.logger (logging)
- app.constants (SUPPORTED_LANGUAGES)
- Python 3.8+ (scripts)

⚠️ **May Need to Install:**
```bash
pip install --upgrade pyqt5-tools
```
(Only if running extraction script manually)

---

## Troubleshooting

### Issue: Import Error "No module named 'app.i18n.translator'"

**Solution:**
1. Verify `app/i18n/translator.py` exists
2. Check that `app/i18n/__init__.py` exists (should already be there)
3. Verify file is in correct location: `c:\Munka\2026\AiWorkFlows\WorkFlow-NameDaysPy\app\i18n\translator.py`

### Issue: ".qm file not found" error at runtime

**Solution:**
1. Run `python ts_to_qm.py` to create `.qm` files
2. Verify files exist: `app/i18n/app_hu.qm`, `app/i18n/app_en.qm`
3. Verify file sizes > 1KB

### Issue: Language not switching

**Solution:**
1. Verify `.qm` files compiled properly (size > 1KB)
2. Check logs for "Loaded translation: hu" message
3. Ensure `switch_language()` is called in settings_dialog
4. May require application restart

---

## Post-Implementation Tasks

After successful implementation:

1. **Add to Version Control:**
   ```bash
   git add app/i18n/translator.py
   git add app/i18n/app_en.ts
   git add app/i18n/app_hu.ts
   git add app/i18n/app_en.qm
   git add app/i18n/app_hu.qm
   git add Docs/100_impl_localization.md
   ```

2. **Update Requirements:**
   - Mark REQ-0045 as IMPLEMENTED
   - Mark REQ-0046 as IMPLEMENTED
   - Add any discovered additional requirements

3. **Document Lessons Learned:**
   - File any issues in project tracking
   - Update localization_dev.md if new insights discovered
   - Note any additional languages to add in future

4. **Future Enhancements:**
   - Add German, French, or other languages (repeat translation process)
   - Implement language selection UI in SettingsDialog if not done
   - Add language switching without restart (if needed)

---

**Document End**  
**Next Step:** Follow Phase 1 to create translator.py and modify code files.
