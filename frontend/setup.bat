@echo off
REM Alumni ML Frontend Setup Script for Windows

echo.
echo ========================================
echo Alumni ML Pipeline - Frontend Setup
echo ========================================
echo.

REM Check Node.js installation
where node >nul 2>nul
if errorlevel 1 (
    echo [X] Node.js is not installed. Please install Node.js 16+ first.
    echo Visit: https://nodejs.org/
    exit /b 1
)

for /f "tokens=*" %%i in ('node --version') do set NODE_VERSION=%%i
echo [OK] Node.js detected: %NODE_VERSION%
echo.

REM Check npm installation
where npm >nul 2>nul
if errorlevel 1 (
    echo [X] npm is not installed.
    exit /b 1
)

for /f "tokens=*" %%i in ('npm --version') do set NPM_VERSION=%%i
echo [OK] npm detected: %NPM_VERSION%
echo.

REM Install dependencies
echo [*] Installing dependencies...
call npm install

echo.
echo [OK] Dependencies installed successfully!
echo.

REM Create .env file if it doesn't exist
if not exist .env (
    echo [*] Creating .env file...
    copy .env.example .env
    echo [OK] .env file created. Please update with your API URL.
) else (
    echo [OK] .env file already exists
)

echo.
echo ========================================
echo [OK] Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Update .env file with your backend API URL
echo 2. Run: npm start
echo.
echo The application will open at http://localhost:3000
echo.

pause
