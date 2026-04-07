Acts as a senior software developer

# Createing and configuring virtual Python environment

## Python version we have to use

- Python 3.10.xxx
- Python location is: "C:\Program Files\Python310"

# Scripts Created

## 1. install_venv.ps1
PowerShell script that creates a virtual environment in the .venv directory.

**Features:**
- Uses Python 3.10 from "C:\Program Files\Python310"
- Creates virtual environment at `.venv` location
- Accepts parameters for customization
- Includes error handling and user-friendly messages

**Usage:**
```powershell
.\tools\install_venv.ps1
```

**Location:** tools/install_venv.ps1

---

## 2. activate_venv.ps1
PowerShell script that activates the virtual environment and opens a new command prompt.

**Features:**
- Activates the virtual environment created by install_venv.ps1
- Displays Python version and executable path
- Validates virtual environment exists before activation
- Accepts custom venv path parameter (default: .venv)
- Includes error handling with helpful messages

**Usage:**
```powershell
.\tools\activate_venv.ps1
```

**Parameters:**
- `-VenvPath`: Path to virtual environment (default: ".venv")

**Location:** tools/activate_venv.ps1

---

## 3. manage_requirements.ps1
PowerShell script that manages Python package dependencies using requirements.txt file.

**Features:**
- Actualizes requirements.txt from the current environment (using `pip freeze`)
- Installs modules from requirements.txt into the current environment
- Default action shows help documentation
- Simple parameter-based operations

**Usage:**
```powershell
# Actualize (freeze) current environment packages to requirements.txt
.\tools\manage_requirements.ps1 -Action actualize

# Install packages from requirements.txt
.\tools\manage_requirements.ps1 -Action install

# Show help (default action)
.\tools\manage_requirements.ps1
.\tools\manage_requirements.ps1 -Action help
```

**Parameters:**
- `-Action`: Operation to perform: `actualize`, `install`, or `help` (default: help)
  - `actualize`: Freezes all packages from current environment to requirements.txt
  - `install`: Installs all packages listed in requirements.txt
  - `help`: Displays usage information

**Examples:**
```powershell
# Generate requirements.txt from your current Python environment
.\tools\manage_requirements.ps1 -Action actualize

# Install all dependencies after cloning the project
.\tools\manage_requirements.ps1 -Action install
```

**Location:** tools/manage_requirements.ps1

## Installation & Usage Steps

### Initial Setup

1. Create the virtual environment (first time only):
   ```powershell
   .\tools\install_venv.ps1
   ```

2. Activate the virtual environment:
   ```powershell
   .\tools\activate_venv.ps1
   ```

3. Install project dependencies:
   ```powershell
   .\tools\manage_requirements.ps1 -Action install
   ```

### Managing Dependencies

After activating the virtual environment, you can manage project dependencies:

**To update requirements.txt from your current environment:**
```powershell
.\tools\manage_requirements.ps1 -Action actualize
```

**To install packages from requirements.txt:**
```powershell
.\tools\manage_requirements.ps1 -Action install
```

**To view help information:**
```powershell
.\tools\manage_requirements.ps1
```