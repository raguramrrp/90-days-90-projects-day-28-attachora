@echo off
setlocal

echo ==============================================================================
echo [ATTACHORA] Starting Attachment Operations Workstation
echo ==============================================================================

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment Python not found. Please run 'setup.bat' first.
    pause
    exit /b 1
)

echo Local Workstation URL: http://localhost:8501
echo Press Ctrl+C in this terminal window to stop the application.
echo.

".venv\Scripts\python.exe" server.py

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] ATTACHORA workstation stopped unexpectedly or failed to launch.
    pause
)
