@echo off
echo Setting up Regulatory Compliance Engine...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Warning: Python is not installed or not in PATH
    echo Please install Python 3.8+ from https://python.org
    echo.
) else (
    echo ✓ Python is installed
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Warning: Node.js is not installed or not in PATH
    echo Please install Node.js 16+ from https://nodejs.org
    echo.
) else (
    echo ✓ Node.js is installed
)

REM Check if npm is installed
npm --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Warning: npm is not installed or not in PATH
    echo.
) else (
    echo ✓ npm is installed
)

echo.
echo Setup complete!
echo.
echo Available commands:
echo - start-backend.bat   - Start only the backend server
echo - start-frontend.bat  - Start only the frontend server
echo - start-all.bat       - Start both backend and frontend
echo - build.bat           - Build for production
echo.
echo Double-click any of these .bat files to run them.
echo.
pause
