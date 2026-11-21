@echo off
setlocal

echo ==============================================================================
echo [ATTACHORA] Resetting Demo Data and Rebuilding Clean Library
echo ==============================================================================

if not exist ".venv\Scripts\activate.bat" (
    echo [ERROR] Virtual environment not found. Please run 'setup.bat' first.
    pause
    exit /b 1
)

call .venv\Scripts\activate.bat

python -c "
import os
import shutil
from pathlib import Path

# Remove existing database and staging
for p in ['attachora.db', '.attachora_staging', 'ATTACHORA_LIBRARY']:
    path = Path(p)
    if path.is_file():
        path.unlink()
        print(f'Removed {p}')
    elif path.is_dir():
        shutil.rmtree(path)
        print(f'Removed folder {p}')

from src.database.db_manager import DB
print('Reinitialized clean database.')
from scripts.generate_sample_emls import create_sample_emails
create_sample_emails()
print('Regenerated sample .eml files.')
"

echo.
echo Demo environment reset successfully!
pause
