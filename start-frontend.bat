@echo off
echo Starting Regulatory Compliance Engine Frontend...
echo.

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Node.js is not installed or not in PATH
    echo Please install Node.js 16+ and try again
    pause
    exit /b 1
)

REM Check if npm is installed
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: npm is not installed or not in PATH
    echo Please install npm and try again
    pause
    exit /b 1
)

REM Navigate to frontend directory
cd /d "%~dp0frontend"

REM Check if node_modules exists, if not install dependencies
if not exist "node_modules" (
    echo Installing dependencies...
    npm install
    if %errorlevel% neq 0 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
) else (
    echo Dependencies already installed, checking for updates...
    npm install
)

REM Start the development server
echo.
echo Starting Vite development server on http://localhost:5173
echo Press Ctrl+C to stop the server
echo.
npm run dev

pause
