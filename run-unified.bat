@echo off
echo Building and running Regulatory Compliance Engine (Unified Architecture)...
echo.

echo Step 1: Building React app...
call npm install
if %errorlevel% neq 0 (
    echo Installation failed!
    pause
    exit /b %errorlevel%
)
call npm run build
if %errorlevel% neq 0 (
    echo Build failed!
    pause
    exit /b %errorlevel%
)

echo.
echo Step 2: Starting Electron app...
call npm run electron

pause
