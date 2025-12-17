# MoSPI Data Portal - Start Server Script

Write-Host "Starting MoSPI Data Portal Infrastructure..." -ForegroundColor Green
Write-Host ""

$venvPython = "C:/Users/Dell/OneDrive/Desktop/Chandu/STATATHON/Statathon 2/.venv/Scripts/python.exe"

# Start the server
Write-Host "Starting FastAPI server on http://127.0.0.1:8080..." -ForegroundColor Cyan
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host ""
Write-Host "📚 API Documentation: http://127.0.0.1:8080/docs" -ForegroundColor Green
Write-Host "📖 Alternative Docs: http://127.0.0.1:8080/redoc" -ForegroundColor Green
Write-Host "❤️  Health Check: http://127.0.0.1:8080/health" -ForegroundColor Green
Write-Host ""

& $venvPython -m uvicorn app.main:app --host 127.0.0.1 --port 8080
