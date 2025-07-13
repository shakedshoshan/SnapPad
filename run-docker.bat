@echo off
REM SnapPad Docker Runner Script for Windows
REM This script sets up X11 forwarding and runs SnapPad in Docker

setlocal enabledelayedexpansion

echo ========================================
echo       SnapPad Docker Runner
echo ========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed. Please install Docker Desktop first.
    echo Download from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

REM Check if Docker Compose is installed
docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker Compose is not installed. Please install Docker Compose first.
    pause
    exit /b 1
)

REM Parse command line arguments
set "command=%~1"
if "%command%"=="" set "command=start"

if "%command%"=="build" goto build
if "%command%"=="run" goto run
if "%command%"=="start" goto start
if "%command%"=="logs" goto logs
if "%command%"=="stop" goto stop
if "%command%"=="help" goto help
if "%command%"=="--help" goto help
if "%command%"=="-h" goto help

echo ERROR: Unknown command: %command%
goto help

:build
echo [INFO] Building SnapPad Docker image...
docker build -t snappad:latest .
if %errorlevel% neq 0 (
    echo ERROR: Failed to build Docker image
    pause
    exit /b 1
)
echo SUCCESS: Docker image built successfully
goto end

:setup_x11
echo [INFO] Setting up X11 forwarding for Windows...
echo.
echo WARNING: Make sure you have an X11 server running:
echo   - VcXsrv (recommended): https://sourceforge.net/projects/vcxsrv/
echo   - Xming: https://sourceforge.net/projects/xming/
echo.
echo Configure your X11 server to:
echo   - Allow connections from localhost
echo   - Disable access control (or add localhost to allowed hosts)
echo.
set "DISPLAY=host.docker.internal:0"
echo [INFO] Set DISPLAY to host.docker.internal:0
echo.

REM Create data directory
if not exist "data" mkdir data
echo [INFO] Created data directory for persistent storage
goto :eof

:run
call :setup_x11
echo [INFO] Running SnapPad in Docker container...

REM Stop existing container if running
docker ps -q -f name=snappad | findstr . >nul 2>&1
if %errorlevel% equ 0 (
    echo [INFO] Stopping existing SnapPad container...
    docker stop snappad >nul 2>&1
    docker rm snappad >nul 2>&1
)

REM Run the container
docker-compose up -d
if %errorlevel% neq 0 (
    echo ERROR: Failed to start SnapPad container
    pause
    exit /b 1
)
echo SUCCESS: SnapPad container started successfully
echo [INFO] Container name: snappad
echo [INFO] To view logs: docker logs snappad
echo [INFO] To stop: docker-compose down
goto end

:start
call :setup_x11
echo [INFO] Building and running SnapPad...
call :build
if %errorlevel% neq 0 goto end
call :run
goto end

:logs
echo [INFO] Showing SnapPad logs...
docker logs -f snappad
goto end

:stop
echo [INFO] Stopping SnapPad container...
docker-compose down
echo SUCCESS: SnapPad container stopped
goto end

:help
echo SnapPad Docker Runner for Windows
echo.
echo Usage: %~nx0 [COMMAND]
echo.
echo Commands:
echo   build     Build the Docker image
echo   run       Run SnapPad in Docker container
echo   start     Build and run SnapPad (default)
echo   logs      Show container logs
echo   stop      Stop the container
echo   help      Show this help message
echo.
echo Prerequisites:
echo   - Docker Desktop installed and running
echo   - X11 server running (VcXsrv, Xming, etc.)
echo.
echo X11 Server Setup:
echo   1. Install VcXsrv or Xming
echo   2. Configure to allow connections from localhost
echo   3. Start the X11 server
echo   4. Run this script
echo.
echo Examples:
echo   %~nx0 start    # Build and run SnapPad
echo   %~nx0 logs     # View application logs
echo   %~nx0 stop     # Stop the application
goto end

:end
echo.
pause 