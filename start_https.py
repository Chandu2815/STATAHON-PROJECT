#!/usr/bin/env python3
"""
HTTPS Server Startup Script for STATAHON Project
Starts the FastAPI server with SSL/TLS encryption
"""
import os
import uvicorn
import ssl
from pathlib import Path

def start_https_server():
    """Start STATAHON server with HTTPS enabled"""
    
    # Check if SSL certificates exist
    cert_file = "server.crt"
    key_file = "server.key"
    
    if not os.path.exists(cert_file) or not os.path.exists(key_file):
        print("❌ SSL certificates not found!")
        print(f"🔍 Looking for: {cert_file} and {key_file}")
        print("📥 Run: python generate_ssl_certificates.py")
        return False
    
    # Server configuration
    port = int(os.environ.get("PORT", 8443))  # Standard HTTPS port
    host = os.environ.get("HOST", "0.0.0.0")
    
    print("🔐 Starting STATAHON HTTPS Server...")
    print(f"📍 Host: {host}")
    print(f"🚪 Port: {port}")
    print(f"🔒 SSL Certificate: {cert_file}")
    print(f"🔑 SSL Private Key: {key_file}")
    print()
    print(f"🌐 Access your secure portal at:")
    print(f"   🔒 https://localhost:{port}")
    print(f"   🔒 https://127.0.0.1:{port}")
    print()
    print("⚠️  Browser Security Notice:")
    print("   Since this is a self-signed certificate, your browser will show")
    print("   a security warning. Click 'Advanced' → 'Proceed to localhost' to continue.")
    print()
    
    try:
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            ssl_keyfile=key_file,
            ssl_certfile=cert_file,
            ssl_version=ssl.PROTOCOL_TLS,
            ssl_cert_reqs=ssl.CERT_NONE,
            reload=True
        )
    except Exception as e:
        print(f"❌ Failed to start HTTPS server: {e}")
        print("💡 Make sure:")
        print("   1. SSL certificates are generated")
        print("   2. Port 8443 is not in use")
        print("   3. You have necessary permissions")
        return False
    
    return True

if __name__ == "__main__":
    start_https_server()