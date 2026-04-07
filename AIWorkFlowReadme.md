# AIWorkFlow-001 User Guide

## Overview
This project uses PowerShell scripts to manage a Python 3.10 virtual environment and project dependencies.

---

## Tools & Scripts

### 1. `tools\install_venv.ps1`
**What it is:** PowerShell script for creating a Python virtual environment  
**What it's for:** Sets up an isolated Python 3.10 environment in the `.venv` directory  

**Usage:**
```powershell
# Default - uses Python 3.10 from C:\Program Files\Python310\python.exe
.\tools\install_venv.ps1

# Custom Python path - specify a different Python installation
.\tools\install_venv.ps1 -PythonPath "C:\Path\To\Your\python.exe"

# Custom venv name
.\tools\install_venv.ps1 -VenvName "my-venv"
```

**Parameters:**
- `-PythonPath`: Full path to python.exe (default: `C:\Program Files\Python310\python.exe`)
- `-VenvName`: Name of virtual environment directory (default: `.venv`)

---

### 2. `tools\activate_venv.ps1`
**What it is:** PowerShell script for activating the virtual environment  
**What it's for:** Activates the `.venv` environment and opens a new PowerShell prompt with the environment active  
**Usage:**
```powershell
.\tools\activate_venv.ps1
```

---

### 3. `tools\python_configurator.md`
**What it is:** Comprehensive configuration and setup documentation  
**What it's for:** Complete reference guide for:
- Python version requirements (Python 3.10)
- Installation instructions for all scripts
- Usage examples and command reference
- Dependency management with `manage_requirements.ps1`

---

## Quick Start

1. **Create virtual environment:**
   ```powershell
   .\tools\install_venv.ps1
   ```

2. **Activate virtual environment:**
   ```powershell
   .\tools\activate_venv.ps1
   ```

3. **For detailed setup and usage refer to:**
   ```
   tools\python_configurator.md
   ```
