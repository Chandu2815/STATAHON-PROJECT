# 🔒 Install Trusted Certificate to Windows

Write-Host "🏛️ Installing STATAHON Government Certificate to Windows Trust Store" -ForegroundColor Cyan
Write-Host ""

# Check if certificate exists
if (!(Test-Path "localhost_trusted.crt")) {
    Write-Host "❌ Certificate file 'localhost_trusted.crt' not found!" -ForegroundColor Red
    Write-Host "📥 Run: python create_trusted_cert.py first" -ForegroundColor Yellow
    exit 1
}

# Install certificate to trusted root store
try {
    Write-Host "📥 Installing certificate..." -ForegroundColor Yellow
    
    # Import certificate to trusted root certification authorities
    Import-Certificate -FilePath "localhost_trusted.crt" -CertStoreLocation "Cert:\LocalMachine\Root"
    
    Write-Host "✅ Certificate successfully installed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "🔒 Your browser will now show HTTPS as secure for:" -ForegroundColor Cyan
    Write-Host "   • https://localhost:8443" -ForegroundColor White
    Write-Host "   • https://127.0.0.1:8443" -ForegroundColor White
    Write-Host ""
    Write-Host "🔄 Restart your browser for changes to take effect" -ForegroundColor Yellow
    
} catch {
    Write-Host "⚠️  Installation failed. You may need to:" -ForegroundColor Red
    Write-Host "   1. Run PowerShell as Administrator" -ForegroundColor Yellow
    Write-Host "   2. Or manually install by double-clicking localhost_trusted.crt" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "📖 Manual installation steps:" -ForegroundColor Cyan
    Write-Host "   1. Double-click localhost_trusted.crt" -ForegroundColor White
    Write-Host "   2. Click 'Install Certificate'" -ForegroundColor White
    Write-Host "   3. Choose 'Local Machine'" -ForegroundColor White
    Write-Host "   4. Select 'Trusted Root Certification Authorities'" -ForegroundColor White
    Write-Host "   5. Click 'Finish'" -ForegroundColor White
}