#!/usr/bin/env powershell
# REVERT TO WORKING STATE
# Run this script if you need to revert to the working backup

Write-Host "🔄 Reverting to backup state..." -ForegroundColor Yellow

# Check if backup exists
if (Test-Path "admin_dashboard_BACKUP_WORKING.html") {
    # Restore the backup
    Copy-Item "admin_dashboard_BACKUP_WORKING.html" -Destination "app\templates\admin_dashboard.html" -Force
    Write-Host "✅ Successfully reverted to working backup!" -ForegroundColor Green
    Write-Host "📊 Current state: Sample data view/export functionality restored" -ForegroundColor Green
    Write-Host "🔗 Server should be running at: http://localhost:8000" -ForegroundColor Cyan
} else {
    Write-Host "❌ Backup file not found!" -ForegroundColor Red
    Write-Host "Expected: admin_dashboard_BACKUP_WORKING.html" -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to continue..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")