@echo off
:: Check if the script is run as Administrator
openfiles >nul 2>nul
if %errorlevel% neq 0 (
    echo This script requires Administrator privileges.
    pause
    exit /b
)

:: Change to the directory where the batch script is located
cd /d "%~dp0"

:: Run the Python script
python telnet.py

pause