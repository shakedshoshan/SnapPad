# QuickSave & Notes - Virtual Environment Setup (PowerShell)
# This script creates a virtual environment and runs the application

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "QuickSave & Notes - Virtual Environment Setup" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "Python not found"
    }
    Write-Host $pythonVersion -ForegroundColor Green
    Write-Host ""
}
catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.x from https://python.org" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if virtual environment already exists
if (Test-Path "quicksave_env\Scripts\Activate.ps1") {
    Write-Host "Virtual environment already exists, activating it..." -ForegroundColor Yellow
} else {
    # Create virtual environment
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    try {
        python -m venv quicksave_env
        if ($LASTEXITCODE -ne 0) {
            throw "Failed to create virtual environment"
        }
        Write-Host "Virtual environment created successfully!" -ForegroundColor Green
        Write-Host ""
    }
    catch {
        Write-Host "ERROR: Failed to create virtual environment" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
try {
    & "quicksave_env\Scripts\Activate.ps1"
    Write-Host "Virtual environment activated!" -ForegroundColor Green
}
catch {
    Write-Host "ERROR: Failed to activate virtual environment" -ForegroundColor Red
    Write-Host "You may need to run: Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip | Out-Null

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
try {
    pip install -r requirements.txt
    if ($LASTEXITCODE -ne 0) {
        throw "Failed to install dependencies"
    }
    Write-Host "Dependencies installed successfully!" -ForegroundColor Green
}
catch {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    Write-Host "Please check your internet connection and try again" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup completed successfully!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Virtual environment is now active." -ForegroundColor Green
Write-Host "You can see '(quicksave_env)' in your prompt." -ForegroundColor Green
Write-Host ""

# Test the application
Write-Host "Testing application..." -ForegroundColor Yellow
try {
    python -c "from main import QuickSaveNotesApp; print('Application modules loaded successfully!')"
    if ($LASTEXITCODE -ne 0) {
        throw "Application test failed"
    }
    Write-Host "Application test passed!" -ForegroundColor Green
}
catch {
    Write-Host "ERROR: Application test failed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "Starting QuickSave & Notes..." -ForegroundColor Green
python main.py

# Keep the virtual environment active
Write-Host ""
Write-Host "Application closed. Virtual environment is still active." -ForegroundColor Yellow
Write-Host "To deactivate, type: deactivate" -ForegroundColor Yellow
Write-Host "To run again, type: python main.py" -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter to exit" 