@echo off
REM Run QuickSave & Notes with administrator privileges

echo Running QuickSave & Notes as administrator...
echo This is necessary for global hotkeys to work correctly.
echo.

REM Check if Python is installed
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Run the application with elevated privileges
powershell -Command "Start-Process py -ArgumentList 'main.py' -Verb RunAs"

echo.
echo Application started with administrator privileges.
echo Check the system tray for the application icon.
echo.
echo Global Hotkeys:
echo   - Ctrl+Alt+S: Toggle dashboard
echo   - Ctrl+Alt+N: Save clipboard as note
echo.

pause 