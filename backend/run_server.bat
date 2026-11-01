@echo off
REM Quick Start Script for Alumni ML Platform with SQLite
REM This script initializes and runs the Flask backend server

echo ======================================================================
echo  Alumni ML Platform - SQLite Integration Quick Start
echo ======================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

REM Install dependencies
echo [1/3] Installing dependencies...
python -m pip install -q Flask-SQLAlchemy SQLAlchemy psycopg2-binary PyJWT >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo      ✓ Dependencies installed

REM Initialize database
echo [2/3] Initializing SQLite database...
if not exist alumni.db (
    python init_db.py
    if %errorlevel% neq 0 (
        echo ERROR: Failed to initialize database
        pause
        exit /b 1
    )
) else (
    echo      ✓ Database already exists (alumni.db)
)

REM Start Flask server
echo.
echo [3/3] Starting Flask server...
echo.
echo      🚀 Server starting at http://localhost:5000
echo      📱 Frontend should be running at http://localhost:3000
echo.
echo      Press Ctrl+C to stop the server
echo.
echo ======================================================================

python app.py
