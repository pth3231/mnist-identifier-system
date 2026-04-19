@echo off
REM Japanese Character Identifier - Development Server Runner (Windows)

echo === Japanese Character Identifier API ===
echo.

cd /d "%~dp0"

REM Check if .env exists
if not exist ".env" (
    echo [!] .env not found. Copying from .env.example...
    copy .env.example .env
    echo [!] Please edit .env with your configuration before running again.
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo [*] Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo [*] Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo [*] Installing dependencies...
pip install -q -e ".[dev]"

REM Run the server
echo [*] Starting development server...
echo.
echo API available at: http://localhost:8000
echo Swagger docs: http://localhost:8000/docs
echo.

uvicorn src.app.main:app --reload --host 0.0.0.0 --port 8000
