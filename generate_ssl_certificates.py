#!/usr/bin/env python3
"""
SSL Certificate Generator for STATAHON Project
Creates self-signed SSL certificates for HTTPS development
"""

import socket
import ssl
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import datetime
import os

def generate_ssl_certificates():
    """Generate self-signed SSL certificates for localhost"""
    
    print("🔐 Generating SSL Certificates for STATAHON HTTPS...")
    
    # Generate private key
    print("🔑 Generating RSA private key...")
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # Generate certificate
    print("📜 Creating SSL certificate...")
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "IN"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Delhi"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "New Delhi"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Ministry of Statistics & Programme Implementation"),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "IT Department"),
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        private_key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.datetime.utcnow()
    ).not_valid_after(
        datetime.datetime.utcnow() + datetime.timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName("localhost"),
            x509.DNSName("127.0.0.1"),
            x509.DNSName("statahon.local"),
        ]),
        critical=False,
    ).sign(private_key, hashes.SHA256())
    
    # Write private key
    print("💾 Saving private key to server.key...")
    with open("server.key", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    # Write certificate
    print("💾 Saving certificate to server.crt...")
    with open("server.crt", "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    
    print("✅ SSL Certificates generated successfully!")
    print(f"📁 Files created in: {os.getcwd()}")
    print("   • server.key (Private Key)")
    print("   • server.crt (SSL Certificate)")
    print()
    print("🔒 Certificate Details:")
    print(f"   • Valid for: 365 days")
    print(f"   • Organization: Ministry of Statistics & Programme Implementation")
    print(f"   • Common Name: localhost")
    print(f"   • Subject Alternative Names: localhost, 127.0.0.1, statahon.local")
    
    return True

if __name__ == "__main__":
    try:
        generate_ssl_certificates()
    except ImportError as e:
        print("❌ Error: Missing cryptography library")
        print("📥 Please install it with: pip install cryptography")
        print(f"💡 Error details: {e}")
    except Exception as e:
        print(f"❌ Error generating certificates: {e}")