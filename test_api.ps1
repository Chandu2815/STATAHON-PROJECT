# Test the API - Run this AFTER starting the server

Write-Host "Testing MoSPI Data Portal API..." -ForegroundColor Green
Write-Host ""

$venvPython = "C:/Users/Dell/OneDrive/Desktop/Chandu/STATATHON/Statathon 2/.venv/Scripts/python.exe"

# Wait a moment for server to be ready
Start-Sleep -Seconds 2

# Run the demo script
& $venvPython demo.py

Write-Host ""
Write-Host "Test complete!" -ForegroundColor Green
