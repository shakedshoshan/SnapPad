@echo off
title SnapPad
echo Starting SnapPad...
echo Press Ctrl+Alt+S to toggle dashboard
echo Look for SnapPad icon in system tray!
echo.

REM Check if Python is available
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please run install.bat first to set up SnapPad
    echo.
    pause
    exit /b 1
)

REM Start SnapPad from Python source
py main.py
pause 