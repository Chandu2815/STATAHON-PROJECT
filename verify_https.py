#!/usr/bin/env python3
"""
HTTPS Verification Script for STATAHON
Tests all secure endpoints and SSL configuration
"""

import ssl
import socket
import urllib.request
import urllib.error
import json
from datetime import datetime

def test_ssl_certificate():
    """Test SSL certificate configuration"""
    try:
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        with socket.create_connection(('localhost', 8443), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname='localhost') as ssock:
                cert = ssock.getpeercert()
                
                print("🔐 SSL Certificate Information:")
                print(f"   Subject: {dict(x[0] for x in cert['subject'])}")
                print(f"   Issuer: {dict(x[0] for x in cert['issuer'])}")
                print(f"   Version: {cert['version']}")
                print(f"   Serial Number: {cert['serialNumber']}")
                print(f"   Not Before: {cert['notBefore']}")
                print(f"   Not After: {cert['notAfter']}")
                
                return True
    except Exception as e:
        print(f"❌ SSL Certificate Test Failed: {e}")
        return False

def test_https_endpoint(url, description):
    """Test a specific HTTPS endpoint"""
    try:
        # Create SSL context that accepts self-signed certificates
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        request = urllib.request.Request(url)
        
        with urllib.request.urlopen(request, context=ssl_context, timeout=10) as response:
            status = response.status
            content_type = response.headers.get('Content-Type', 'Unknown')
            
            if status == 200:
                print(f"✅ {description}")
                print(f"   URL: {url}")
                print(f"   Status: {status}")
                print(f"   Content-Type: {content_type}")
                return True
            else:
                print(f"⚠️  {description} - Unexpected status: {status}")
                return False
                
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"⚠️  {description} - Page not found (404)")
        else:
            print(f"❌ {description} - HTTP Error {e.code}")
        return False
    except Exception as e:
        print(f"❌ {description} - Error: {e}")
        return False

def main():
    """Run HTTPS verification tests"""
    
    print("🔒 STATAHON HTTPS Verification")
    print(f"🕒 Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # Test SSL Certificate
    print("\n📋 Testing SSL Certificate...")
    ssl_ok = test_ssl_certificate()
    
    print("\n📋 Testing HTTPS Endpoints...")
    
    # Define endpoints to test
    endpoints = [
        ("https://localhost:8443/", "Home Page"),
        ("https://localhost:8443/login", "User Login Page"),
        ("https://localhost:8443/admin/login", "Admin Login Page"),
        ("https://localhost:8443/register", "User Registration Page"),
        ("https://localhost:8443/docs", "API Documentation"),
        ("https://localhost:8443/openapi.json", "OpenAPI Specification"),
    ]
    
    # Test each endpoint
    passed = 0
    total = len(endpoints)
    
    for url, description in endpoints:
        if test_https_endpoint(url, description):
            passed += 1
        print()  # Add blank line between tests
    
    # Summary
    print("=" * 60)
    print("📊 HTTPS Test Summary:")
    print(f"   SSL Certificate: {'✅ Valid' if ssl_ok else '❌ Invalid'}")
    print(f"   Endpoints Tested: {total}")
    print(f"   Endpoints Passed: {passed}")
    print(f"   Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total and ssl_ok:
        print("\n🎉 All HTTPS tests passed! Your STATAHON portal is secure!")
        print("🔒 Access your secure portal at: https://localhost:8443")
        print("⚠️  Remember to click 'Advanced' → 'Proceed' on browser security warning")
    else:
        print(f"\n⚠️  Some tests failed. Please check the HTTPS configuration.")
        print("💡 Common issues:")
        print("   1. Server not running on port 8443")
        print("   2. SSL certificates missing or invalid")
        print("   3. Firewall blocking HTTPS port")

if __name__ == "__main__":
    main()