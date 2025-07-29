@echo off
echo Building Regulatory Compliance Engine for Production...
echo.

REM Build Backend
echo Building backend...
cd /d "%~dp0backend"

REM Activate virtual environment if it exists
if exist "venv" (
    call venv\Scripts\activate.bat
    echo Virtual environment activated
) else (
    echo Warning: No virtual environment found
)

echo Backend is ready for production deployment
echo.

REM Build Frontend
echo Building frontend...
cd /d "%~dp0frontend"

REM Check if dependencies are installed
if not exist "node_modules" (
    echo Installing dependencies...
    npm install
    if %errorlevel% neq 0 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Build the frontend
echo Creating production build...
npm run build
if %errorlevel% neq 0 (
    echo Error: Failed to build frontend
    pause
    exit /b 1
)

echo.
echo Build completed successfully!
echo - Frontend build is in: frontend/dist/
echo - Backend is ready for production deployment
echo.
echo To preview the production build, run: npm run preview (from frontend directory)
echo.
pause
