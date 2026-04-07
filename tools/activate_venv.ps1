# PowerShell Script to activate the virtual environment and open a new prompt
# Activates the virtual environment created by install_venv.ps1

param(
    [string]$VenvPath = ".venv"
)

$ActivateScript = Join-Path (Join-Path $VenvPath "Scripts") "Activate.ps1"

# Check if virtual environment exists
if (-not (Test-Path $ActivateScript)) {
    Write-Error "Virtual environment not found at: $VenvPath"
    Write-Host "Please run install_venv.ps1 first to create the virtual environment" -ForegroundColor Yellow
    exit 1
}

Write-Host "Activating virtual environment from: $VenvPath" -ForegroundColor Green

# Activate the virtual environment
& $ActivateScript

Write-Host "Virtual environment activated successfully!" -ForegroundColor Green
Write-Host "Python executable: $(where.exe python)" -ForegroundColor Cyan
Write-Host "Python version: $(python --version)" -ForegroundColor Cyan
