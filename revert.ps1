#!/usr/bin/env powershell
<#
REVERT SCRIPT FOR STATAHON-PROJECT
==================================
This script reverts the login.html to its original backup version.

Usage: 
1. Run from STATAHON-PROJECT directory
2. Simply type: .\revert.ps1
or just type: revert

This will restore the login.html file to the original version before security enhancements.
#>

Write-Host "🔄 STATAHON Security Revert Tool" -ForegroundColor Cyan
Write-Host "=================================" -ForegroundColor Cyan
Write-Host ""

# Check if backup exists
$backupPath = "app\templates\login_backup_original.html"
$loginPath = "app\templates\login.html"

if (Test-Path $backupPath) {
    Write-Host "✅ Backup file found: $backupPath" -ForegroundColor Green
    
    # Create a timestamp backup of current version
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $currentBackup = "app\templates\login_enhanced_$timestamp.html"
    Copy-Item $loginPath $currentBackup -Force
    Write-Host "📦 Current enhanced version backed up as: $currentBackup" -ForegroundColor Yellow
    
    # Restore original
    Copy-Item $backupPath $loginPath -Force
    Write-Host "🔙 Login page reverted to original version successfully!" -ForegroundColor Green
    Write-Host ""
    Write-Host "✅ Original login.html has been restored" -ForegroundColor Green
    Write-Host "✅ Enhanced version saved as backup: $currentBackup" -ForegroundColor Green
    Write-Host ""
    Write-Host "🌐 Restart your server to see the changes:" -ForegroundColor Cyan
    Write-Host "   python start.py" -ForegroundColor White
    
} else {
    Write-Host "❌ Backup file not found: $backupPath" -ForegroundColor Red
    Write-Host "Cannot revert without original backup!" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Revert completed!" -ForegroundColor Green