@echo off
setlocal

echo ==============================================================================
echo [ATTACHORA] Running Automated QA & Unit Test Suite
echo ==============================================================================

if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found. Please run 'setup.bat' first.
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat

python -m pytest tests -v --tb=short

if %ERRORLEVEL% equ 0 (
    echo.
    echo ==============================================================================
    echo [ATTACHORA] ALL TESTS PASSED! (Status: PASS)
    echo ==============================================================================
) else (
    echo.
    echo ==============================================================================
    echo [ATTACHORA] TEST FAILURES DETECTED! (Status: FAIL)
    echo ==============================================================================
    exit /b 1
)
