@echo off
REM Alumni ML Platform - Startup Script for Windows
REM This script starts both the Flask backend and React frontend

echo.
echo ===============================================
echo  Alumni ML Platform - Starting Services
echo ===============================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js not found. Please install Node.js 14+
    pause
    exit /b 1
)

echo [1/4] Checking directories...
if not exist "backend" (
    echo [ERROR] backend/ directory not found
    pause
    exit /b 1
)

if not exist "frontend" (
    echo [ERROR] frontend/ directory not found
    pause
    exit /b 1
)

echo        ✓ Directories verified

echo.
echo [2/4] Installing/Checking Python dependencies...
cd backend
pip install -q Flask Flask-CORS PyJWT python-dotenv
cd ..
echo        ✓ Python dependencies ready

echo.
echo [3/4] Installing/Checking Node.js dependencies...
cd frontend
if not exist "node_modules" (
    echo        Installing npm packages (this may take a minute)...
    npm install --silent
)
cd ..
echo        ✓ Node.js dependencies ready

echo.
echo [4/4] Starting services...
echo.

REM Start Flask backend in new window
echo Starting Flask Backend on http://localhost:5000
start "Alumni ML Platform - Backend" cmd /k "cd backend && python app.py"

REM Wait a few seconds for backend to start
timeout /t 3 /nobreak

REM Start React frontend in new window
echo Starting React Frontend on http://localhost:3000
start "Alumni ML Platform - Frontend" cmd /k "cd frontend && npm start"

echo.
echo ===============================================
echo  Services Started!
echo ===============================================
echo.
echo Backend (Flask):  http://localhost:5000
echo Frontend (React): http://localhost:3000
echo.
echo Test credentials:
echo   Email: user@alumni.edu
echo   Password: user123
echo.
echo Press Ctrl+C in either window to stop.
echo.
pause
