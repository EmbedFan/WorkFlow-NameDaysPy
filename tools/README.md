# Tools Directory - Usage Guide

This directory contains utility scripts and configuration tools for managing the NameDays Monitoring Application development and deployment.

## Available Tools

### 1. **activate_venv.ps1** - Virtual Environment Activation
**Type:** PowerShell Script  
**Purpose:** Activate the Python virtual environment and open a new PowerShell prompt

**Usage:**
```powershell
.\activate_venv.ps1
```

**What it does:**
- Activates `.venv` virtual environment
- Opens new PowerShell window with activated environment
- All subsequent Python commands use isolated dependencies

**When to use:**
- Starting development session
- Running Python scripts in isolation
- Installing/updating packages

---

### 2. **install_venv.ps1** - Virtual Environment Setup
**Type:** PowerShell Script  
**Purpose:** Create and initialize Python virtual environment

**Usage:**
```powershell
.\install_venv.ps1
```

**What it does:**
- Creates `.venv/` directory if not exists
- Installs Python virtual environment
- Activates the environment
- Installs requirements from `requirements.txt`

**When to use:**
- First-time setup
- After deleting `.venv` directory
- Setting up development environment on new machine

**Requirements:**
- Python 3.7+ installed and in PATH
- `pip` package manager available

---

### 3. **manage_requirements.ps1** - Dependencies Manager
**Type:** PowerShell Script  
**Purpose:** Manage Python dependencies and requirements.txt

**Usage:**
```powershell
# Show help
.\manage_requirements.ps1 -Action help

# Freeze current environment packages to requirements.txt
.\manage_requirements.ps1 -Action actualize

# Install packages from requirements.txt
.\manage_requirements.ps1 -Action install
```

**Actions:**

- **actualize** - Updates `requirements.txt` with all installed packages
  ```powershell
  .\manage_requirements.ps1 -Action actualize
  ```
  - Runs `pip freeze` and saves to `requirements.txt`
  - Overwrites existing file
  - Use after `pip install new-package`

- **install** - Installs all packages from `requirements.txt`
  ```powershell
  .\manage_requirements.ps1 -Action install
  ```
  - Runs `pip install -r requirements.txt`
  - Installs exact versions specified

- **help** - Display usage information (default)
  ```powershell
  .\manage_requirements.ps1
  .\manage_requirements.ps1 -Action help
  ```

**When to use:**
- Installing dependencies from clean virtual environment
- Updating requirements after adding new packages
- Synchronizing packages across development machines

---

### 4. **python_configurator.md** - Python Configuration Guide
**Type:** Markdown Document  
**Purpose:** Documentation for Python environment configuration

**Usage:**
- Open in text editor or Markdown viewer
- Read setup and configuration instructions
- Reference for Python version requirements
- Development environment setup guide

**When to use:**
- Initial Python setup
- Troubleshooting Python configuration issues
- Understanding environment requirements

---

### 5. **create_release.py** - Release Package Manager
**Type:** Python Script (REQ-0066)  
**Purpose:** Manage file associations and create release packages

**Usage:**
```powershell
python tools/create_release.py <command> [options]
```

**Commands:**

- **list** - List all 47 file associations
  ```powershell
  python tools/create_release.py list
  ```
  - Shows install/ to source file mappings
  - Groups by module (app, core, i18n, etc.)
  - Indicates file existence status

- **verify** - Verify files match between install/ and source
  ```powershell
  python tools/create_release.py verify
  ```
  - Checks all file associations
  - Reports matches, mismatches, missing files
  - Shows coverage percentage
  - Uses SHA256 for binary files, text comparison for code

- **sync** - Synchronize files from source to install/
  ```powershell
  python tools/create_release.py sync
  ```
  - Copies modified files from source to install/
  - Skips unchanged files
  - Creates parent directories as needed
  - Reports: copied, skipped, errors

- **package** - Create timestamped release package
  ```powershell
  # Default name
  python tools/create_release.py package

  # Custom name
  python tools/create_release.py package MyApp-v1.0
  ```
  - Creates: `releases/NameDaysApp-Release_<timestamp>/`
  - Copies: complete `install/` directory
  - Generates: `MANIFEST.json` with file mappings
  - Generates: `PACKAGE_README.md` with documentation
  - Ready for distribution

- **report** - Generate detailed release report
  ```powershell
  python tools/create_release.py report
  ```
  - Shows file statistics
  - Lists module breakdown
  - Calculates coverage percentage
  - Identifies discrepancies

**File Associations (47 files):**
- Root: 4 files (main.py, setup.py, README.md, requirements.txt)
- App Core: 5 files
- Core Module: 4 files (monitoring, notifications)
- I18N Module: 7 files (translations: English, Hungarian)
- Managers: 4 files (contacts, namedays, settings)
- Services: 4 files (email, validation, Windows integration)
- UI: 8 files (dialogs and system tray)
- Utils: 5 files (logging, dates, files)
- Resources: 5 files (CSV database, icons, stylesheets)

**When to use:**
- Before creating release version
- Syncing changes to install/ directory
- Verifying deployment package integrity
- Creating distribution packages
- Generating release reports

**Output Examples:**

```
========================================
FILE ASSOCIATIONS - Install/ to Source Mapping
========================================

[APP] - 5 files
  [py] ✓ ✓ app/__init__.py                    <- app/__init__.py
  [py] ✓ ✓ app/constants.py                   <- app/constants.py
  ...

TOTAL: 47 files
```

---

## Typical Workflow

### Initial Development Setup
```powershell
cd WorkFlow-NameDaysPy

# 1. Create virtual environment
.\tools\install_venv.ps1

# 2. Activate environment
.\tools\activate_venv.ps1

# 3. Start developing
python main.py
```

### After Adding New Dependencies
```powershell
# 1. Install with pip
pip install numpy

# 2. Update requirements.txt
.\tools\manage_requirements.ps1 -Action actualize

# 3. Sync to install/ directory
python tools/create_release.py sync
```

### Creating a Release
```powershell
# 1. Verify all files match
python tools/create_release.py verify

# 2. Sync any changes
python tools/create_release.py sync

# 3. Create release package
python tools/create_release.py package NameDaysApp-v1.0

# 4. Generate report
python tools/create_release.py report
```

### Setting Up on New Machine
```powershell
# Clone repository, then:

# 1. Install virtual environment
.\tools\install_venv.ps1

# 2. Activate environment
.\tools\activate_venv.ps1

# 3. Run application
python main.py
```

---

## File Locations & References

| Tool | Type | Language | Dependencies |
|------|------|----------|--------------|
| activate_venv.ps1 | Script | PowerShell | .venv/ |
| install_venv.ps1 | Script | PowerShell | Python, pip |
| manage_requirements.ps1 | Script | PowerShell | pip |
| python_configurator.md | Document | Markdown | - |
| create_release.py | Script | Python 3.7+ | pathlib, json, hashlib, shutil |

---

## Troubleshooting

**Q: What if PowerShell scripts won't execute?**
```powershell
# Set execution policy (one per machine)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Q: Requirements.txt not updating?**
```powershell
# Ensure venv is activated
.\tools\activate_venv.ps1
pip list                    # Verify current packages
.\tools\manage_requirements.ps1 -Action actualize
```

**Q: Sync failing with permission errors?**
```powershell
# Check file permissions
icacls C:\Munka\2026\AiWorkFlows\WorkFlow-NameDaysPy\install

# Run PowerShell as Administrator if needed
```

---

## Environment Variables

The tools automatically set:
- `VIRTUAL_ENV` - Points to .venv directory
- `PATH` - Updated to include .venv/Scripts
- `PYTHONHOME` - Set to virtual environment

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Command not recognized / General error |
| 2 | File not found / Permission denied |

---

## Related Documentation

- Main application: [README.md](../README.md)
- Release files list: [Docs/files_shall_be_released.md](../Docs/files_shall_be_released.md)
- Requirements: [Docs/requirements.md](../Docs/requirements.md)
- Python configuration: [python_configurator.md](./python_configurator.md)

---

**Last Updated:** April 7, 2026  
**Version:** 1.0.0  
**Application:** NameDays Monitoring App [REQ-0066]
