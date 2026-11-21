@echo off
setlocal enabledelayedexpansion

echo ==============================================================================
echo [ATTACHORA] Setting Up Intelligent Email Attachment Classification and Filing System
echo ==============================================================================

:: Check Python
where python >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not found on PATH. Please install Python 3.11+ and retry.
    exit /b 1
)

echo [1/4] Checking Python environment...
if not exist ".venv" (
    echo Creating project virtual environment...
    python -m venv --system-site-packages .venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        exit /b 1
    )
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)

echo [2/4] Installing dependencies...
".venv\Scripts\python.exe" -m pip install -r requirements.txt

echo [3/4] Generating realistic sample .EML email test suite...
".venv\Scripts\python.exe" scripts\generate_sample_emls.py

echo [4/4] Initializing ATTACHORA SQLite database and default filing rules...
".venv\Scripts\python.exe" -c "from src.database.db_manager import DB; print('ATTACHORA database initialized successfully with default rules.')"

echo.
echo ==============================================================================
echo [ATTACHORA] Setup Completed Successfully!
echo Run 'run.bat' to start the workstation interface.
echo Run 'test.bat' to execute automated test suite.
echo ==============================================================================
pause
