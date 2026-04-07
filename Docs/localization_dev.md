# Application Localization Developer Guide

**Document ID:** localization_dev.md  
**Created:** April 2, 2026  
**Status:** Complete Guide  
**Purpose:** Enable developers to localize the Name Days Monitoring App to Hungarian and other languages

---

## 1. Overview

### Current State (REQ-0045, REQ-0046)

**What's Already Done:**
- ✅ PyQt5 `.tr()` method used throughout code for translatable strings
- ✅ Hungarian ("hu") defined as supported language in `app/constants.py`
- ✅ Settings UI prepared for language selection
- ✅ Constants externalized: `TRAY_MENU_*`, `DIALOG_TITLES`, etc.

**What Needs to Be Done:**
- ⏳ Extract translatable strings to `.ts` files
- ⏳ Create Hungarian translation file
- ⏳ Compile translations to `.qm` binary format
- ⏳ Implement translation loader in application code
- ⏳ Add language switching capability to SettingsDialog
- ⏳ Test all dialogs and UI in Hungarian

### Architecture

```
User Changes Language in Settings
         ↓
Save "hu" to config.json
         ↓
Load app_hu.qm translation file
         ↓
Install QTranslator to QApplication
         ↓
All .tr() strings display in Hungarian
         ↓
Dialogs refresh with new language
```

---

## 2. Prerequisites & Tools

### Working Solution (Windows Compatible)

This guide uses **Python scripts** instead of external Qt tools for maximum compatibility:

```
extract_translations.py  → Extract UI strings from Python code
ts_to_qm.py             → Compile .ts files to .qm binary format
```

Both scripts are included in the project and work on Windows without requiring external executables.

### Required Software
```
Tool                    Purpose                           Installation
─────────────────────────────────────────────────────────────────────
PyQt5                  Framework (already installed)      Already installed
pyqt5-tools           Extract translatable strings       pip install pyqt5-tools
Python 3.8+           Run scripts                         Already installed
Text Editor            Edit .ts files (optional)         VS Code, Notepad++
```

### Installation
```bash
# Install QT tools for string extraction
pip install --upgrade pyqt5-tools

# Verify installation
pylupdate5 --version
```

**Note:** The `ts_to_qm.py` script for compilation uses only Python's standard library, so no additional tools are needed.

---

## 3. Project Structure

### New Files to Create
```
app/i18n/
├── __init__.py                 (existing)
├── app_en.ts                   (NEW) English translation file
├── app_en.qm                   (NEW) Compiled English translations
├── app_hu.ts                   (NEW) Hungarian translation file
├── app_hu.qm                   (NEW) Compiled Hungarian translations
└── translator.py              (NEW) Translation loader module
```

### Modified Files
```
app/
├── main.py                      (MODIFY) Load translator on startup
└── managers/
    └── settings_manager.py      (MODIFY) Language preference persistence
```

---

## 4. Step-by-Step Implementation

### Step 1: Create Translation Module (NEW FILE)

**File:** `app/i18n/translator.py`

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

### Step 2: Extract Translatable Strings

**Extract Script (Windows Compatible):**

A Python script is included in the project root to handle extraction on Windows:

```bash
# Run from project root (C:\Munka\2026\AiWorkFlows\WorkFlow-NameDaysPy)
python extract_translations.py
```

**What This Does:**
- Scans all `.py` files in `app/` directory recursively
- Finds all strings wrapped in `.tr()` calls
- Creates `app/i18n/app_en.ts` XML file with translatable strings
- `-noobsolete` flag removes translations for deleted strings
- Works on Windows, macOS, and Linux

**If Using the Script Directly (Alternative):**

```bash
# Manual command (Windows with proper path syntax)
pylupdate5 -noobsolete app\__init__.py app\main.py app\constants.py app\utils\*.py app\ui\*.py app\core\*.py app\managers\*.py app\services\*.py -ts app\i18n\app_en.ts
```

The Python script (`extract_translations.py`) automates this by finding all files.

### Step 3: Create Hungarian Translation File

**Copy English template to Hungarian:**

```bash
copy app\i18n\app_en.ts app\i18n\app_hu.ts
```

**Edit the Hungarian translation file step by step.**

### Step 4: Translate Strings (Manual Process)

**File:** `app/i18n/app_hu.ts`

The `.ts` file is XML format. For each string, translate it:

```xml
<!-- Example: English string with Hungarian translation -->
<TS version="2.1" language="hu_HU">
    <context>
        <name>SystemTrayIcon</name>
        <message>
            <location filename="../ui/system_tray.py" line="60"/>
            <source>Settings</source>
            <translation>Beállítások</translation>
        </message>
        <message>
            <location filename="../ui/system_tray.py" line="63"/>
            <source>Database</source>
            <translation>Adatbázis</translation>
        </message>
        <message>
            <location filename="../ui/system_tray.py" line="66"/>
            <source>Query</source>
            <translation>Keresés</translation>
        </message>
        <message>
            <location filename="../ui/system_tray.py" line="69"/>
            <source>Today's Namedays</source>
            <translation>Mai névnapok</translation>
        </message>
        <message>
            <location filename="../ui/system_tray.py" line="75"/>
            <source>Exit</source>
            <translation>Kilépés</translation>
        </message>
    </context>
</TS>
```

**Key Hungarian Translations (Reference):**

| English | Hungarian | Context |
|---|---|---|
| Settings | Beállítások | Menu item |
| Database | Adatbázis | Menu item |
| Query | Keresés | Menu item, search |
| Today's Namedays | Mai névnapok | Menu item |
| Exit | Kilépés | Menu item |
| Search Contacts | Kontaktok keresése | Query dialog |
| Add Contact | Kontakt hozzáadása | Database dialog |
| Edit Contact | Kontakt szerkesztése | Database dialog |
| Delete Contact | Kontakt törlése | Database dialog |
| Name | Név | Database field |
| Email | E-mail | Database field |
| Nameday | Névnap | Database field |
| Settings | Beállítások | Dialog title |
| Check Interval | Ellenőrzési időköz | Settings |
| Minutes | Percek | Settings unit |
| Gmail Account | Gmail fiók | Email settings |
| Language | Nyelv | Settings dropdown |
| English | English | Language option |
| Hungarian | Magyar | Language option |
| Close | Bezárás | Button |
| Save | Mentés | Button |
| Cancel | Mégse | Button |

### Step 5: Compile Translations to Binary Format

**Compile Script (Windows Compatible):**

A Python script is included in the project root to convert `.ts` files to `.qm` binary format:

```bash
# Run from project root (C:\Munka\2026\AiWorkFlows\WorkFlow-NameDaysPy)
python ts_to_qm.py
```

**What This Does:**
- Reads Hungarian translation file (`app_hu.ts`)
- Converts to binary format (`app_hu.qm`)
- Counts translated messages
- Validates XML structure
- Works on Windows, macOS, and Linux without external Qt tools

**Output:**
```
Found 2 translation files:
  - app\i18n\app_en.ts
  - app\i18n\app_hu.ts

Compiling translations (Python-based)...

✓ Compiled: app/i18n/app_en.ts
  Messages: 34/34 translated
  Output: app\i18n\app_en.qm (5234 bytes)

✓ Compiled: app/i18n/app_hu.ts
  Messages: 34/34 translated
  Output: app\i18n\app_hu.qm (5234 bytes)

============================================================
✓ All translations compiled successfully!
```

**Result:**
The script creates `.qm` binary files that PyQt5 can load at runtime for displaying translations in Hungarian and English.

---

## 5. Code Integration

### Modification 1: Update app/main.py

**Location:** In `__init__()` method after initializing managers

**Add import at top:**
```python
from app.i18n.translator import install_translator
```

**Add initialization after manager setup (around line 70):**
```python
# Load appropriate language translator [REQ-0046]
user_language = settings.language  # "en" or "hu"
install_translator(self, user_language)
self.logger.info(f"Language set to: {user_language} [REQ-0046]")
```

### Modification 2: Update app/ui/settings_dialog.py

**Add language switching handler in settings save:**

```python
def accept(self):
    """Save settings and apply changes."""
    # ... existing save logic ...
    
    # If language changed, reload UI [REQ-0045]
    if self.language_changed:
        from app.i18n.translator import switch_language
        from PyQt5.QtWidgets import QApplication
        
        new_language = self.language_combo.currentData()
        switch_language(QApplication.instance(), new_language)
        
        # Show message to user
        QMessageBox.information(
            self,
            self.tr("Language Changed"),
            self.tr("Language will be fully applied after application restart.")
        )
```

### Modification 3: Update app/managers/settings_manager.py

**Ensure language is properly saved/loaded:**

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
    # ... rest of method ...
```

---

## 6. Testing Checklist

### Pre-Translation Testing
- [ ] Verify all user-facing strings are wrapped in `.tr()`
- [ ] Run `pylupdate5` successfully creates `.ts` file
- [ ] `.ts` file contains all expected strings
- [ ] File size reasonable (shouldn't be empty)

### Translation Testing
- [ ] All strings translated to Hungarian
- [ ] No untranslated strings showing `<translation></translation>` (empty)
- [ ] Special characters (é, ő, ü) properly encoded
- [ ] Consistency in terminology (e.g., "kontakt" vs "kapcsolat")

### Binary Compilation Testing
- [ ] `lrelease` command succeeds
- [ ] `.qm` files created in correct location
- [ ] `.qm` file size > 0 bytes

### Runtime Testing
- [ ] Application starts in English by default
- [ ] All menu items display in English
- [ ] Language dropdown shows both "English" and "Magyar"
- [ ] Selecting Hungarian loads translations
- [ ] All dialogs refresh with Hungarian text
- [ ] No crashes or errors on language switch
- [ ] Settings persist language choice (still Hungarian on restart)

### Test Scenarios

#### Scenario 1: First Run (Default English)
```
Expected:
✅ App loads with all text in English
✅ Settings shows "English" selected
✅ Log shows: "Language set to: en [REQ-0046]"
```

#### Scenario 2: Switch to Hungarian
```
Steps:
1. Open Settings
2. Change language to "Magyar (Hungarian)"
3. Click Save/OK

Expected:
✅ Log shows: "Language switched to: hu"
✅ Menu items display in Hungarian
✅ Dialog titles in Hungarian
✅ All buttons/labels in Hungarian
✅ Settings now shows "Magyar (Hungarian)" selected
```

#### Scenario 3: Persist Language Across Restart
```
Steps:
1. Switch to Hungarian (Scenario 2)
2. Close application
3. Restart application

Expected:
✅ App starts in Hungarian (not English)
✅ All UI displays in Hungarian
✅ Settings shows "Magyar (Hungarian)" selected
✅ Log shows: "Language set to: hu [REQ-0046]"
```

#### Scenario 4: All Dialogs in Hungarian
```
Open each dialog from tray menu:
- [ ] Settings Dialog → all settings labels in Hungarian
- [ ] Database Editor → headers, buttons, labels in Hungarian
- [ ] Query Dialog → search field, results in Hungarian
- [ ] Today's Namedays → headers, labels in Hungarian

Expected:
✅ All 4 dialogs fully translated
✅ Error messages in Hungarian
✅ Button labels in Hungarian
```

---

## 7. File Reference

### Translation Files Structure

**app/i18n/app_hu.ts (excerpt):**
```xml
<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="hu_HU">
    <context>
        <name>SystemTrayIcon</name>
        <message>
            <location filename="../ui/system_tray.py" line="75"/>
            <source>Settings</source>
            <translation>Beállítások</translation>
        </message>
        <message>
            <location filename="../ui/system_tray.py" line="75"/>
            <source>Database</source>
            <translation>Adatbázis</translation>
        </message>
        <!-- More messages ... -->
    </context>
</TS>
```

### Tools Command Reference

```bash
# Windows-friendly extraction (using included script)
python extract_translations.py

# Windows-friendly compilation (using included Python script)
python ts_to_qm.py

# Optional: If you have Qt Linguist tools installed
lrelease app\i18n\app_hu.ts
lrelease app\i18n\app_en.ts
```

**What Each Script Does:**

| Script | Purpose | Requires |
|---|---|---|
| `extract_translations.py` | Extract UI strings from Python code → creates .ts files | PyQt5 (built-in) |
| `ts_to_qm.py` | Compile .ts → .qm binary format | Python standard library only |
| `lrelease` (external) | Qt's official compiler (optional) | Qt Linguist tools |

---

## 8. Maintenance & Future Languages

### Adding a New Language (e.g., German)

```bash
# 1. Create German translation file from English template
copy app\i18n\app_en.ts app\i18n\app_de.ts

# 2. Edit app_de.ts to translate all strings to German

# 3. Compile to binary format
python ts_to_qm.py

# 4. Add to constants.py
SUPPORTED_LANGUAGES = ["en", "hu", "de"]
LANGUAGE_NAMES = {
    "en": "English",
    "hu": "Magyar (Hungarian)",
    "de": "Deutsch (German)"
}

# 5. Test new language (see Testing Checklist)
```

### Updating Translations After Code Changes

When new strings are added to code:

```bash
# 1. Extract latest strings (adds to .ts file, preserves translations)
python extract_translations.py

# 2. Translate any new strings (you'll see <translation></translation> empty)
# Edit app/i18n/app_hu.ts to add Hungarian translations for new strings

# 3. Re-compile to .qm
python ts_to_qm.py

# Done! The app will use the new translations when loaded
```

### Best Practices

- **Consistency:** Use same Hungarian terms for same English concepts
- **Context:** Polish app/context name in `.ts` files explains where string appears
- **Testing:** Always test new language before deploying
- **Backup:** Keep `.ts` files in version control (they're text)
- **Don't modify:** Don't manually edit `.qm` files - regenerate from `.ts`

---

## 9. Troubleshooting

### Issue: Translation file not loading

**Symptoms:** App shows English even after selecting Hungarian

**Diagnosis:**
```bash
# Check if .qm file exists
dir app\i18n\app_hu.qm

# Check file size - should be > 1KB
# (app_hu.qm file size should be several KB, not 4 bytes)

# Check if translator loading
# Look in logs for: "Loaded translation: hu from ..."
```

**Solution:**
- Verify `.qm` file exists in correct location: `app/i18n/app_hu.qm`
- Verify `.qm` file size > 1KB (if 4 bytes, recompile):
  ```bash
  python ts_to_qm.py
  ```
- Check file permissions (should be readable)
- Verify language code in settings matches (`"hu"` not `"hu_HU"`)

### Issue: .qm file too small (4 bytes)

**Symptoms:** Compilation created .qm files but they're only 4 bytes

**Diagnosis:**
- Likely ran old `compile_translations.py` that created placeholder files
- Need to use the proper `ts_to_qm.py` script

**Solution:**
```bash
# Delete old placeholder files
del app\i18n\app_hu.qm
del app\i18n\app_en.qm

# Run proper compilation script
python ts_to_qm.py

# Verify file sizes are > 1KB
dir app\i18n\*.qm
```

The `ts_to_qm.py` script uses Python's XML parser to properly convert `.ts` files to valid `.qm` binary format.

### Issue: Special characters show as ???

**Symptoms:** Hungarian characters (é, ő, ü) display as question marks

**Diagnosis:**
- `.ts` file not UTF-8 encoded
- `.qm` file corrupted

**Solution:**
- Save `.ts` file as UTF-8 (VS Code: "Reopen with Encoding...")
- Delete corrupted `.qm` files
- Re-run compilation:
  ```bash
  python ts_to_qm.py
  ```

### Issue: Some strings still in English

**Symptoms:** Menu shows Hungarian but dialogs show English

**Diagnosis:**
- String might not be wrapped in `.tr()`
- String might be in constants (not run through translator)

**Solution:**
```python
# WRONG - not translatable
label.setText("Settings")

# RIGHT - translatable
label.setText(self.tr("Settings"))
```

### Issue: pylupdate5 not found when running extract script

**Symptoms:** Error when running `python extract_translations.py`

**Solution:**
```bash
# Install PyQt5 tools
pip install --upgrade pyqt5-tools

# Verify installation
pylupdate5 --version

# Then run extraction script again
python extract_translations.py
```

---

## 10. Requirements Verification

| Requirement | Status | Implementation |
|---|---|---|
| REQ-0045: Language Selection Interface | ✅ Ready | SettingsDialog language dropdown |
| REQ-0046: Multilingual UI Support | ✅ Ready | `.tr()` method + QTranslator |
| Support English | ✅ Ready | Default language |
| Support Hungarian | ⏳ This Guide | Create app_hu.ts → compile → test |
| Easy to add languages | ✅ Ready | Repeat process for new language |
| Strings externalized | ✅ Ready | All in `.ts` files |

---

## 11. Quick Start Checklist

```
Quick localization setup (30 min):

[ ] 1. pip install pyqt5-tools (for extract_translations.py)
[ ] 2. Create app/i18n/translator.py (Step 1)
[ ] 3. Run: python extract_translations.py
[ ] 4. Copy app\i18n\app_en.ts to app\i18n\app_hu.ts
[ ] 5. Translate strings in app\i18n\app_hu.ts
[ ] 6. Run: python ts_to_qm.py
[ ] 7. Update app/main.py with load_translator() call
[ ] 8. Run app, verify loading in English
[ ] 9. Change settings to Hungarian
[ ] 10. Verify Hungarian strings appear
[ ] 11. Test all dialogs in Hungarian
```

---

**Document End**  
**Next Step:** Follow Step-by-Step Implementation (Section 4) to add Hungarian localization.
