# PowerShell Script to install Python virtual environment
# Creates a virtual environment in the .venv directory using Python 3.10

param(
    [string]$PythonPath = "C:\Program Files\Python310\python.exe",
    [string]$VenvName = ".venv"
)

# Check if Python exists at the specified location
if (-not (Test-Path $PythonPath)) {
    Write-Error "Python not found at: $PythonPath"
    exit 1
}

Write-Host "Creating virtual environment at: $VenvName" -ForegroundColor Green
Write-Host "Using Python from: $PythonPath" -ForegroundColor Cyan

# Create the virtual environment
& $PythonPath -m venv $VenvName

if ($LASTEXITCODE -eq 0) {
    Write-Host "Virtual environment created successfully!" -ForegroundColor Green
    Write-Host "To activate the environment, run: .\activate_venv.ps1" -ForegroundColor Yellow
} else {
    Write-Error "Failed to create virtual environment"
    exit 1
}
