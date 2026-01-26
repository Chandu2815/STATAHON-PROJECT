# Admin Portal Security Revert Script (PowerShell)
# Usage: Run "powershell .\REVERT_ADMIN_SECURITY.ps1" or just "revert-admin"

Write-Host "🔄 Reverting Admin Portal to Original Version..." -ForegroundColor Cyan

# Check if backup exists
if (!(Test-Path "app\templates\admin_login_backup.html")) {
    Write-Host "❌ Error: No backup found!" -ForegroundColor Red
    Write-Host "Cannot revert - admin_login_backup.html not found" -ForegroundColor Red
    exit 1
}

# Create current backup before reverting
Write-Host "📦 Creating backup of current enhanced version..." -ForegroundColor Yellow
Copy-Item "app\templates\admin_login.html" "app\templates\admin_login_enhanced_backup.html" -Force

# Restore original
Write-Host "♻️  Restoring original admin login..." -ForegroundColor Green
Copy-Item "app\templates\admin_login_backup.html" "app\templates\admin_login.html" -Force

Write-Host "✅ Admin portal reverted to original version!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Available admin login versions:" -ForegroundColor Blue
Write-Host "   • admin_login.html (current - original)" -ForegroundColor White
Write-Host "   • admin_login_backup.html (original backup)" -ForegroundColor White  
Write-Host "   • admin_login_enhanced_backup.html (enhanced backup)" -ForegroundColor White
Write-Host ""
Write-Host "🔄 To re-enable enhanced security:" -ForegroundColor Cyan
Write-Host "   Copy-Item admin_login_enhanced_backup.html admin_login.html -Force" -ForegroundColor White

# Create alias for easy access
Set-Alias -Name "revert-admin" -Value "REVERT_ADMIN_SECURITY.ps1"