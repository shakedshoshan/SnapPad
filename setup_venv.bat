@echo off
REM QuickSave & Notes - Virtual Environment Setup
REM This script creates a virtual environment and runs the application

echo ========================================
echo QuickSave & Notes - Virtual Environment Setup
echo ========================================
echo.

REM Check if Python is installed
echo Checking Python installation...
py --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.x from https://python.org
    pause
    exit /b 1
)

py --version
echo.

REM Check if virtual environment already exists
if exist "quicksave_env\Scripts\activate.bat" (
    echo Virtual environment already exists, activating it...
    goto :activate_env
)

REM Create virtual environment
echo Creating virtual environment...
py -m venv quicksave_env
if %errorlevel% neq 0 (
    echo ERROR: Failed to create virtual environment
    pause
    exit /b 1
)

echo Virtual environment created successfully!
echo.

:activate_env
REM Activate virtual environment
echo Activating virtual environment...
call quicksave_env\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
py -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
py -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)

echo.
echo ========================================
echo Setup completed successfully!
echo ========================================
echo.
echo Virtual environment is now active.
echo You can see "(quicksave_env)" in your prompt.
echo.

REM Test the application
echo Testing application...
python -c "from main import QuickSaveNotesApp; print('Application modules loaded successfully!')"
if %errorlevel% neq 0 (
    echo ERROR: Application test failed
    pause
    exit /b 1
)

echo.
echo Starting QuickSave & Notes...
python main.py

REM Keep the virtual environment active
echo.
echo Application closed. Virtual environment is still active.
echo To deactivate, type: deactivate
echo To run again, type: python main.py
echo.
cmd /k 