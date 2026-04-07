# Files Shall Be Released

## Application Files Required for Deployment

### Root Level
- `main.py` - Main entry point
- `requirements.txt` - Python dependencies
- `setup.py` - Setup configuration
- `README.md` - Application documentation
- `AIWorkFlowReadme.md` - Workflow documentation

### Application Core (app/)
- `app/__init__.py`
- `app/constants.py`
- `app/exceptions.py`
- `app/main.py` - Alternative entry point
- `app/types.py`

### Core Module (app/core/)
- `app/core/__init__.py`
- `app/core/monitoring_engine.py`
- `app/core/notification_manager.py`
- `app/core/notification_queue.py`

### Internationalization (app/i18n/)
- `app/i18n/__init__.py`
- `app/i18n/app_hu.ts` - Hungarian translations source
- `app/i18n/app_hu.qm` - Hungarian translations compiled (must be recompiled from .ts)

### Managers Module (app/managers/)
- `app/managers/__init__.py`
- `app/managers/contact_db_manager.py`
- `app/managers/nameday_reference_manager.py` - Enhanced with REQ-0066 reload functionality
- `app/managers/settings_manager.py`

### Services Module (app/services/)
- `app/services/__init__.py`
- `app/services/data_validator.py`
- `app/services/email_service.py`
- `app/services/windows_startup.py`

### UI Module (app/ui/)
- `app/ui/__init__.py`
- `app/ui/database_editor_dialog.py`
- `app/ui/notification_modal.py`
- `app/ui/query_dialog.py`
- `app/ui/settings_dialog.py`
- `app/ui/system_tray.py` - Enhanced with REQ-0066 reload menu item
- `app/ui/today_namedays_dialog.py`

### Utilities Module (app/utils/)
- `app/utils/__init__.py`
- `app/utils/date_utils.py`
- `app/utils/error_handler.py`
- `app/utils/file_utils.py`
- `app/utils/logger.py`

### Configuration (config/)
- `config/config.json` - Application configuration

### Resources (resources/)
- `resources/namedays.csv` - Nameday reference database
- `resources/styles/default.qss` - Qt stylesheet

### Optional Documentation
- `Docs/IMPLEMENTATION_REPORT.md`
- `Docs/implementation.md`
- `Docs/requirements.md` - Contains all requirements including REQ-0066
- `Docs/system_design.md`
- `Docs/006_impl_add_db_reload_to_tray.md` - REQ-0066 implementation plan

## Files to Exclude from Release
- `.venv/` - Virtual environment directory (users create their own)
- `app/__pycache__/` - Python bytecode cache
- `app/core/__pycache__/` - Python bytecode cache
- `app/managers/__pycache__/` - Python bytecode cache
- `app/services/__pycache__/` - Python bytecode cache
- `app/ui/__pycache__/` - Python bytecode cache
- `app/utils/__pycache__/` - Python bytecode cache
- `.git/` - Version control (if applicable)
- `logs/` - User-generated logs
- `data/` - User data (contacts database, etc.)

## Pre-Deployment Steps

1. **Compile Hungarian Translations**
   ```powershell
   C:\Qt\Qt5.12.12\5.12.12\msvc2017_64\bin\lrelease.exe app\i18n\app_hu.ts -qm app\i18n\app_hu.qm
   ```

2. **Verify Translation Binary Exists**
   - Ensure `app/i18n/app_hu.qm` is present and up-to-date

3. **Test application startup**
   ```powershell
   python main.py
   ```

4. **Verify REQ-0066 Feature**
   - Right-click system tray icon
   - Verify "Reload Namedays Database" menu item appears
   - Test reload functionality

## Critical Notes for Release

### Translation System
- Translator reference retention is critical: `app._translator = translator` must be maintained in code
- .qm binary file must be freshly compiled from latest app_hu.ts before release
- Translator installation must occur BEFORE UI components are created

### REQ-0066 Implementation
- NamedayReferenceManager.reload() added with proper error handling
- SystemTrayIcon includes "Reload Namedays Database" menu item with notification feedback
- Hungarian translations added for all REQ-0066 UI strings

### Entry Points
- `main.py` - Root entry point (recommended)
- `app/main.py` - Direct app module entry point (requires path setup in app/main.py)

### Dependencies
- Install from requirements.txt: `pip install -r requirements.txt`
- Primary: PyQt5, PyYAML, etc.

## Minimum Viable Release Package
If space is limited, include:
- All files in app/ directory except __pycache__
- config/config.json
- resources/namedays.csv
- resources/styles/default.qss
- requirements.txt
- main.py
- README.md
