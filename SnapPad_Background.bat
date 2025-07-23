@echo off
title SnapPad Background Service

REM Check if Python is available
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please run install.bat first to set up SnapPad
    echo.
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found
    echo Please run install.bat first to set up SnapPad
    echo.
    pause
    exit /b 1
)

REM Run SnapPad using pythonw.exe (Windows GUI version) instead of python.exe
REM This runs without requiring a console window
start "" "venv\Scripts\pythonw.exe" main.py

REM Show brief confirmation and exit
echo SnapPad is now running in the background.
echo Look for the SnapPad icon in your system tray.
echo To stop SnapPad, use Task Manager and end the "pythonw.exe" process.
echo.
echo This window will close in 3 seconds...
timeout /t 3 /nobreak >nul
exit 