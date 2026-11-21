@echo off
setlocal

echo ==============================================================================
echo [ATTACHORA] Starting Attachment Operations Workstation
echo ==============================================================================

if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found. Please run 'setup.bat' first.
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat

echo Local Workstation URL: http://localhost:8501
echo Press Ctrl+C in this terminal window to stop the application.
echo.

streamlit run app.py --server.port 8501 --server.headless false

if %ERRORLEVEL% neq 0 (
    echo.
    echo [ERROR] ATTACHORA workstation stopped unexpectedly or failed to launch.
    pause
)
