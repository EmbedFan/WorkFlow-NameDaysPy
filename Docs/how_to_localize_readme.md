# Developer Guide: Qt Localization (.ts → .qm)

## Overview

This guide explains how to create and compile Qt translation files for the Name Days Monitoring application.

- **`.ts` files**: Human-readable XML source files with translatable strings
- **`.qm` files**: Compiled binary files used by the Qt runtime

## Step 1: Extract Translatable Strings from Code

### Using the Extraction Script

The `extract_translations.py` script scans Python files and extracts all strings marked with `.tr()` calls.

```bash
# From project root:
python extract_translations.py
```

### What It Does
- Scans `app/` directory for `self.tr("...")` calls
- Extracts all strings with their context (dialog class name)
- Creates `app/i18n/app_en.ts` with English source strings

### Example Output
```xml
<context>
    <name>AddEditContactDialog</name>
    <message>
        <source>Edit Contact</source>
    </message>
    <message>
        <source>Add New Contact</source>
    </message>
</context>
```

## Step 2: Create Translation Files

### Generate Translation File for New Language

Use Qt Linguist or manually create a `.ts` file by copying `app_en.ts`:

```bash
# Copy English source to create Hungarian translation file
copy app\i18n\app_en.ts app\i18n\app_hu.ts
```

### Edit Translations in Qt Linguist

1. Open Qt Linguist (if installed)
2. Open `app/i18n/app_hu.ts`
3. For each message:
   - View source string
   - Enter Hungarian translation
   - Mark as "Done" when complete

### Manual XML Editing

Edit `app/i18n/app_hu.ts` directly if Qt Linguist is unavailable:

```xml
<context>
    <name>AddEditContactDialog</name>
    <message>
        <source>Edit Contact</source>
        <translation>Kapcsolat szerkesztése</translation>
    </message>
</context>
```

**Note**: Save in UTF-8 encoding

## Step 3: Compile .ts to .qm

### Option A: Using lrelease Command Line (Recommended)

The `lrelease` tool is part of Qt development tools.

#### Finding lrelease

If Qt is installed, lrelease should be at:
```
<Qt_Installation>/bin/lrelease.exe
```

Common locations:
- `C:\Qt\Qt5.12.12\5.12.12\msvc2017_64\bin\lrelease.exe`
- `/opt/qt5/bin/lrelease` (Linux/Mac)
- `C:\Program Files\Qt\5.15.0\msvc2019_64\bin\lrelease.exe`

#### Compile Single File

```bash
lrelease.exe app\i18n\app_hu.ts -qm app\i18n\app_hu.qm
```

#### Compile All Files

```bash
lrelease.exe app\i18n\app_en.ts -qm app\i18n\app_en.qm
lrelease.exe app\i18n\app_hu.ts -qm app\i18n\app_hu.qm
```

#### Expected Output

```
Updating 'app\i18n\app_hu.qm'...
    Generated 49 translation(s) (49 finished and 0 unfinished)
```

### Option B: Batch Compilation Script

Create `compile_qm_files.bat` in project root:

```batch
@echo off
REM Set Qt path (modify if needed)
set LRELEASE="C:\Qt\Qt5.12.12\5.12.12\msvc2017_64\bin\lrelease.exe"

REM Compile all .ts files
for %%f in (app\i18n\*.ts) do (
    echo Compiling %%f...
    %LRELEASE% %%f -qm %%~dpnf.qm
)

echo Done!
```

Run with:
```bash
compile_qm_files.bat
```

### Option C: Using Python Script (if lrelease unavailable)

```bash
python compile_translations.py
```

**Note**: This requires lrelease.exe to be available this may not work without proper Qt installation.

## Step 4: Verify Compiled Files

### Check File Size

Compiled `.qm` files should be reasonably sized:
- English `.qm`: typically 16-100 bytes (source language)
- Translated `.qm`: typically 1KB-10KB (depending on translation volume)

```bash
# Check file sizes
dir app\i18n\*.qm
```

### Test Loading in Python

```python
from PyQt5.QtCore import QTranslator

translator = QTranslator()
loaded = translator.load('app/i18n/app_hu.qm')
print(f"Loaded: {loaded}")
print(f"Empty: {translator.isEmpty()}")

# Test a translation
result = translator.translate("AddEditContactDialog", "Edit Contact")
print(f"Translation: {result}")
```

## Workflow Summary

```
1. Code with i18n
   ↓
2. extract_translations.py
   ↓
3. app_en.ts (created automatically)
   ↓
4. Copy to app_hu.ts
   ↓
5. Translate in Qt Linguist (or manually)
   ↓
6. lrelease.exe app_hu.ts -qm app_hu.qm
   ↓
7. app_hu.qm (ready to use!)
   ↓
8. Restart app with language set to "hu"
```

## Integration in Application

### Code Requirements

Mark all translatable strings with `.tr()`:

```python
# In PyQt5 dialogs
self.button.setText(self.tr("Save"))
self.label.setText(self.tr("Contact Name"))
```

### Configuration

The app loads translations based on `config/config.json`:

```json
{
  "language": "hu"
}
```

### Translator Module

The `app/i18n/translator.py` module handles loading:

```python
from app.i18n.translator import install_translator

# In app/__main__.py startup:
install_translator(app, user_language)
```

## Troubleshooting

### Issue: "lrelease not found"

**Solution**: 
1. Install Qt development tools from https://www.qt.io/download
2. OR use Qt online service (Weblate, Crowdin)
3. OR use online .ts to .qm converter

### Issue: Qt won't load .qm file

**Check**:
- File exists: `dir app\i18n\*.qm`
- File size is not suspiciously small (less than 50 bytes)
- Use official `lrelease` tool to compile
- Test with Python:
  ```python
  from pathlib import Path
  print(Path('app/i18n/app_hu.qm').stat().st_size)
  ```

### Issue: Translations not appearing in UI

**Check**:
1. Language set correctly in `config.json`
2. `.qm` file loaded successfully (check logs)
3. String exists in `.qm` file with exact context and source text
4. Application restarted after language change

## Files Reference

| File | Purpose |
|------|---------|
| `extract_translations.py` | Extract `.tr()` strings from code → `app_en.ts` |
| `app_en.ts` | English source strings (auto-generated) |
| `app_hu.ts` | Hungarian translations (manual translation) |
| `app_en.qm` | Compiled English (fallback) |
| `app_hu.qm` | Compiled Hungarian (runtime use) |
| `app/i18n/translator.py` | Translation loader module |

## Adding New Languages

To add a new language (e.g., German):

1. **Extract strings** (if code changed):
   ```bash
   python extract_translations.py
   ```

2. **Create translation file**:
   ```bash
   copy app\i18n\app_en.ts app\i18n\app_de.ts
   ```

3. **Translate in Qt Linguist**:
   - Open `app_de.ts`
   - Translate all messages to German

4. **Compile**:
   ```bash
   lrelease.exe app\i18n\app_de.ts -qm app\i18n\app_de.qm
   ```

5. **Update Settings UI** (app/ui/settings_dialog.py):
   - Add "Deutsch" to language dropdown with code "de"

6. **Update Settings Manager** (app/managers/settings_manager.py):
   - Add "de" to SUPPORTED_LANGUAGES

## Resources

- Qt Linguist Documentation: https://doc.qt.io/qt-5/qtlinguist-index.html
- `.ts` File Format: https://doc.qt.io/qt-5/linguist-ts-file-format.html
- lrelease Tool: https://doc.qt.io/qt-5/linguist-lrelease.html
- Qt i18n Best Practices: https://doc.qt.io/qt-5/i18n-source-translation.html
