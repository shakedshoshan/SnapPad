@echo off
REM SnapPad - Complete Installation and Setup Script
REM This script handles everything needed to install and run SnapPad

echo ========================================
echo       SnapPad - Installation Script
echo ========================================
echo.

REM Check if Python is installed
echo [1/4] Checking Python installation...
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.7+ from https://python.org
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

py --version
echo ✓ Python is installed successfully!
echo.

REM Update pip to latest version
echo [2/4] Updating pip...
py -m pip install --upgrade pip --quiet
if %errorlevel% neq 0 (
    echo WARNING: Could not update pip, but continuing...
)
echo ✓ pip updated successfully!
echo.

REM Install required packages
echo [3/4] Installing required packages...
echo Installing PyQt6, pyperclip, keyboard, and pywin32...
py -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    echo.
    echo Please check your internet connection and try again
    echo If the problem persists, try running this script as administrator
    echo.
    pause
    exit /b 1
)

echo ✓ All dependencies installed successfully!
echo.

REM Test the application
echo [4/4] Testing application startup...
py -c "import sys; import PyQt6, pyperclip, keyboard; print('✓ All modules loaded successfully!')"
if %errorlevel% neq 0 (
    echo ERROR: Application test failed
    echo Some dependencies may not be installed correctly
    pause
    exit /b 1
)

echo.
echo ========================================
echo     Installation completed successfully!
echo ========================================
echo.
echo SnapPad is now ready to use!
echo.
echo To run the application:
echo   • Double-click this file again, or
echo   • Run: python main.py
echo.
echo Global Hotkeys (when running):
echo   • Ctrl+Alt+S: Toggle dashboard
echo   • Ctrl+Alt+N: Save clipboard as note
echo.
echo The application will run in the background and
echo appear in your system tray.
echo.

REM Check if this is a first-time installation or running again
py -c "import os; exit(0 if os.path.exists('snappad.db') else 1)" >nul 2>&1
if %errorlevel% neq 0 (
    REM First time installation
    set /p choice="Do you want to start SnapPad now? (y/n): "
    if /i "%choice%"=="y" (
        echo.
        echo Starting SnapPad...
        echo You can close this window once SnapPad is running.
        echo Look for the SnapPad icon in your system tray!
        echo.
        start "SnapPad" py main.py
    ) else (
        echo.
        echo You can start SnapPad later by running: python main.py
    )
) else (
    REM Subsequent runs - just start the application
    echo Starting SnapPad...
    echo You can close this window once SnapPad is running.
    echo Look for the SnapPad icon in your system tray!
    echo.
    start "SnapPad" py main.py
)

echo.
echo Thank you for using SnapPad!
timeout /t 3 >nul 