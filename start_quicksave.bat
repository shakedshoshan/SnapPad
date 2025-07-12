@echo off
REM QuickSave & Notes - Windows Launcher
REM This batch file starts the QuickSave & Notes application

echo Starting QuickSave & Notes...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.x from https://python.org
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking dependencies...
python -c "import PyQt6, pyperclip, keyboard" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing required packages...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Start the application
echo Starting QuickSave & Notes...
python main.py

REM Keep console open if there was an error
if %errorlevel% neq 0 (
    echo.
    echo Application exited with error code %errorlevel%
    pause
) 