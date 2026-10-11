# NMVS Startup Script (PowerShell)
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  Starting NMVS Enterprise Telemetry Engine" -ForegroundColor Cyan
Write-Host "  Backend API + Frontend Console" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

Set-Location "$PSScriptRoot\backend"

Write-Host "[1/2] Opening NMVS Dashboard in browser..." -ForegroundColor Yellow
Start-Process "http://127.0.0.1:8000/ui"

Write-Host "[2/2] Starting FastAPI server on http://127.0.0.1:8000 ..." -ForegroundColor Green
Write-Host "Press Ctrl+C anytime to stop the server.`n" -ForegroundColor DarkGray

& ".\.venv\Scripts\uvicorn.exe" main:app --reload --host 127.0.0.1 --port 8000
