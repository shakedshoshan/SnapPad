@echo off
REM SnapPad - Installation and Setup Script
REM This script installs all dependencies and guides the user to use SnapPad.bat

echo ========================================
echo       SnapPad - Installation Script
echo ========================================
echo.

REM Check if Python is installed
echo [1/3] Checking Python installation...
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
echo [2/3] Updating pip...
py -m pip install --upgrade pip --quiet
if %errorlevel% neq 0 (
    echo WARNING: Could not update pip, but continuing...
)
echo ✓ pip updated successfully!
echo.

REM Install required packages
echo [3/3] Installing required packages...
echo Installing dependencies from requirements.txt...
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

echo ========================================
echo     Installation completed successfully!
echo ========================================
echo.
echo SnapPad is now ready to use!
echo.
echo To run the application:
echo   • Double-click SnapPad.bat

echo Or run from the command line:
echo   • SnapPad.bat

echo Global Hotkeys (when running):
echo   • Ctrl+Alt+S: Toggle dashboard
echo   • Ctrl+Alt+N: Save clipboard as note
echo.
echo The application will run in the background and
echo appear in your system tray.
echo.
echo Thank you for installing SnapPad!
echo.
pause
exit /b 0 