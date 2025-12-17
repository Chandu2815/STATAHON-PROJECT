# Start MoSPI Data Portal Server
Write-Host "Starting MoSPI Data Portal Infrastructure..." -ForegroundColor Cyan

# Check if virtual environment exists
if (-not (Test-Path ".venv\Scripts\python.exe")) {
    Write-Host "Error: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run: python -m venv .venv" -ForegroundColor Yellow
    exit 1
}

# Activate virtual environment and start server
Write-Host "Activating virtual environment..." -ForegroundColor Green
& ".venv\Scripts\python.exe" -m uvicorn app.main:app --host 0.0.0.0 --port 8080

Write-Host "`nServer stopped." -ForegroundColor Yellow
