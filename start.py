#!/usr/bin/env python3
"""
STATAHON Server Startup Script
Supports both HTTP and HTTPS modes with SSL certificates
Environment variables:
- PORT: Server port (default: 8000 for HTTP, 8443 for HTTPS)
- HOST: Server host (default: 0.0.0.0)
- USE_HTTPS: Enable HTTPS mode (default: False)
"""
import os
import uvicorn
import ssl
from pathlib import Path

def check_ssl_certificates():
    """Check if SSL certificates exist"""
    cert_file = "server.crt"
    key_file = "server.key"
    return os.path.exists(cert_file) and os.path.exists(key_file)

def start_server():
    """Start STATAHON server with optional HTTPS support"""
    
    # Check if HTTPS is requested
    use_https = os.environ.get("USE_HTTPS", "false").lower() == "true"
    
    # Set default ports based on protocol
    if use_https:
        default_port = 8443  # Standard HTTPS port
    else:
        default_port = 8001  # Standard HTTP port
    
    # Railway provides PORT as an environment variable
    port = int(os.environ.get("PORT", default_port))
    host = os.environ.get("HOST", "0.0.0.0")
    
    # SSL Configuration
    ssl_keyfile = None
    ssl_certfile = None
    
    if use_https:
        if check_ssl_certificates():
            # Use trusted certificate if available, otherwise self-signed
            if os.path.exists("localhost_trusted.key") and os.path.exists("localhost_trusted.crt"):
                ssl_keyfile = "localhost_trusted.key"
                ssl_certfile = "localhost_trusted.crt"
                protocol = "HTTPS 🏛️ (Trusted)"
                print(f"🏛️ Using government-issued trusted certificate")
            else:
                ssl_keyfile = "server.key"
                ssl_certfile = "server.crt"
                protocol = "HTTPS 🔒 (Self-signed)"
                print(f"⚠️  Using self-signed certificate")
        else:
            print("⚠️  HTTPS requested but SSL certificates not found!")
            print("📥 Run: python generate_ssl_certificates.py")
            print("🔄 Falling back to HTTP mode...")
            use_https = False
            protocol = "HTTP"
    else:
        protocol = "HTTP"
    
    # Server startup
    print(f"🚀 Starting STATAHON {protocol} Server")
    print(f"📍 Host: {host}")
    print(f"🚪 Port: {port}")
    
    if use_https:
        print(f"🔒 SSL Certificate: {ssl_certfile}")
        print(f"🔑 SSL Private Key: {ssl_keyfile}")
        print(f"🌐 Secure Access: https://localhost:{port}")
        print("⚠️  Browser will show security warning for self-signed certificate")
    else:
        print(f"🌐 Access: http://localhost:{port}")
    
    print()
    
    try:
        uvicorn_config = {
            "app": "app.main:app",
            "host": host,
            "port": port,
            "reload": False,  # Disable reload in production
            "workers": 1,
            "access_log": True
        }
        
        # Add SSL configuration if HTTPS is enabled
        if use_https and ssl_keyfile and ssl_certfile:
            uvicorn_config.update({
                "ssl_keyfile": ssl_keyfile,
                "ssl_certfile": ssl_certfile,
                "ssl_version": ssl.PROTOCOL_TLS,
                "ssl_cert_reqs": ssl.CERT_NONE
            })
        
        uvicorn.run(**uvicorn_config)
        
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        print("💡 Troubleshooting:")
        print(f"   1. Check if port {port} is available")
        print("   2. Verify SSL certificates (if using HTTPS)")
        print("   3. Check file permissions")

if __name__ == "__main__":
    start_server()
