@echo off
title NMVS - Network Monitoring and Visualization System
echo ======================================================================
echo   Starting NMVS Enterprise Telemetry Engine
echo   Backend API + Frontend Console
echo ======================================================================
echo.
cd /d "%~dp0backend"

echo [1/2] Opening NMVS Dashboard in browser...
start http://127.0.0.1:8000/ui

echo [2/2] Starting FastAPI server on http://127.0.0.1:8000 ...
echo Press Ctrl+C anytime to stop the server.
echo.
.\.venv\Scripts\uvicorn.exe main:app --reload --host 127.0.0.1 --port 8000
pause
