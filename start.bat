@echo off
REM Quick start script for Windows
echo ================================================
echo   LEGAL COURT AI - QUICK START
echo ================================================
echo.

REM Activate conda environment
call conda activate legal-court-ai
if errorlevel 1 (
    echo Error: Could not activate conda environment
    echo Please create it first: conda create -n legal-court-ai python=3.11
    pause
    exit /b 1
)

REM Run the application
python start.py

pause
