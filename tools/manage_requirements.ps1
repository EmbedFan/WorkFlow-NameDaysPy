param(
    [string]$Action = "help"
)

function Show-Help {
    Write-Host "Python Requirements Manager" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage: .\manage_requirements.ps1 -Action <action>" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Actions:" -ForegroundColor Green
    Write-Host "  actualize - Freeze current environment packages to requirements.txt"
    Write-Host "  install   - Install packages from requirements.txt"
    Write-Host "  help      - Display this help message (default)"
    Write-Host ""
}

function Actualize-Requirements {
    Write-Host "Actualizing requirements from current environment..." -ForegroundColor Green
    
    if (Test-Path "requirements.txt") {
        Write-Host "Updating existing requirements.txt..." -ForegroundColor Yellow
    } else {
        Write-Host "Creating new requirements.txt..." -ForegroundColor Yellow
    }
    
    try {
        pip freeze | Out-File -FilePath "requirements.txt" -Encoding UTF8
        Write-Host "Successfully actualized requirements.txt" -ForegroundColor Green
        Write-Host ""
        Write-Host "First 5 packages:" -ForegroundColor Cyan
        Get-Content "requirements.txt" -TotalCount 5
    } catch {
        Write-Error "Failed to actualize requirements: $_"
        exit 1
    }
}

function Install-Requirements {
    if (-not (Test-Path "requirements.txt")) {
        Write-Error "requirements.txt not found"
        exit 1
    }

    Write-Host "Installing packages from requirements.txt..." -ForegroundColor Green
    
    pip install -r "requirements.txt"
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "Successfully installed all packages" -ForegroundColor Green
    } else {
        Write-Error "Failed to install requirements"
        exit 1
    }
}

switch ($Action.ToLower()) {
    "actualize" {
        Actualize-Requirements
    }
    "install" {
        Install-Requirements
    }
    "help" {
        Show-Help
    }
    default {
        Write-Host "Unknown action: $Action" -ForegroundColor Red
        Show-Help
        exit 1
    }
}
