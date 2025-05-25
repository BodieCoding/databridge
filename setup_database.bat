@echo off
REM DataBridge SQL Server Setup Helper
REM This script runs the setup_sqlserver.py script with default settings

echo DataBridge SQL Server Setup
echo ===========================

REM Check if Python is installed
python --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Python is not installed or not in PATH
    echo Please install Python 3.6 or higher
    pause
    exit /b 1
)

REM Check if Docker is installed
docker --version > nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Docker is not installed or not in PATH
    echo Please install Docker Desktop and make sure it's running
    pause
    exit /b 1
)

echo Starting SQL Server setup...
python setup_sqlserver.py %*

if %ERRORLEVEL% NEQ 0 (
    echo Setup failed
    pause
    exit /b 1
)

echo Setup completed successfully!
echo You can now connect to the database using:
echo   Server: localhost,1433
echo   Username: sa
echo   Password: DataBridge2025! (unless you specified a different one)
echo   Database: pocdb

pause
