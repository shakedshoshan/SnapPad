@echo off

REM Check if Python is available (silently)
py --version >nul 2>&1
if %errorlevel% neq 0 (
    exit /b 1
)

REM Check if virtual environment exists (silently)
if not exist "venv\Scripts\activate.bat" (
    exit /b 1
)

REM Run SnapPad using pythonw.exe (Windows GUI version) 
REM This runs completely in background without any console window
start "" "venv\Scripts\pythonw.exe" main.py

REM Exit immediately without showing any messages
exit /b 0 