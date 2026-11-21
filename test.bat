@echo off
setlocal

echo ==============================================================================
echo [ATTACHORA] Running Automated QA and Unit Test Suite
echo ==============================================================================

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment Python not found. Please run setup.bat first.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" -m pytest tests -v --tb=short
set TEST_STATUS=%ERRORLEVEL%

if %TEST_STATUS% equ 0 (
    echo.
    echo ==============================================================================
    echo [ATTACHORA] ALL TESTS PASSED! Status: PASS
    echo ==============================================================================
    exit /b 0
) else (
    echo.
    echo ==============================================================================
    echo [ATTACHORA] TEST FAILURES DETECTED! Status: FAIL
    echo ==============================================================================
    exit /b 1
)
