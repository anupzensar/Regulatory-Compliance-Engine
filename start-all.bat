@echo off
echo Starting Both Backend and Frontend Services...
echo.

REM Start backend in a new window
echo Starting backend server...
start "Backend - Regulatory Compliance Engine" cmd /k "%~dp0start-backend.bat"

REM Wait a few seconds for backend to start
timeout /t 5 /nobreak >nul

REM Start frontend in a new window
echo Starting frontend server...
start "Frontend - Regulatory Compliance Engine" cmd /k "%~dp0start-frontend.bat"

echo.
echo Both services are starting in separate windows:
echo - Backend: http://localhost:7000
echo - Frontend: http://localhost:5173
echo - API Docs: http://localhost:7000/docs
echo.
echo Close this window or press any key to exit...
pause >nul
