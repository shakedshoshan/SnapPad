@echo off
REM QuickSave & Notes - Installation and Setup Script
REM This script sets up the application for first-time use

echo ========================================
echo QuickSave & Notes - Setup Script
echo ========================================
echo.

REM Check if Python is installed
echo Checking Python installation...
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.x from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

py --version
echo Python is installed successfully!
echo.

REM Install required packages
echo Installing required packages...
py -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    echo.
    echo Please check your internet connection and try again
    pause
    exit /b 1
)

echo.
echo Dependencies installed successfully!
echo.

REM Test the application
echo Testing application startup...
timeout /t 2 >nul
py -c "from main import QuickSaveNotesApp; print('Application modules loaded successfully!')"
if %errorlevel% neq 0 (
    echo ERROR: Application test failed
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo You can now run the application using:
echo   - Double-click "start_quicksave.bat"
echo   - Or run "python main.py" from command line
echo.
echo Global Hotkeys:
echo   - Ctrl+Alt+S: Toggle dashboard
echo   - Ctrl+Alt+N: Save clipboard as note
echo.
echo The application will run in the background and
echo appear in your system tray.
echo.

REM Ask if user wants to start the application now
set /p choice="Do you want to start the application now? (y/n): "
if /i "%choice%"=="y" (
    echo.
    echo Starting QuickSave & Notes...
    py main.py
)

echo.
echo Thank you for using QuickSave & Notes!
pause 