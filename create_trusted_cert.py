import ssl
import socket
from cryptography import x509
from cryptography.x509.oid import NameOID, ExtendedKeyUsageOID
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
import datetime
import ipaddress

def create_trusted_certificate():
    """Create a more trusted SSL certificate for localhost"""
    
    # Generate private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # Create certificate
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COUNTRY_NAME, "IN"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "New Delhi"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "New Delhi"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Ministry of Statistics and Programme Implementation"),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, "STATAHON Data Portal"),
        x509.NameAttribute(NameOID.COMMON_NAME, "localhost"),
    ])
    
    # Build certificate
    cert_builder = x509.CertificateBuilder()
    cert_builder = cert_builder.subject_name(subject)
    cert_builder = cert_builder.issuer_name(issuer)
    cert_builder = cert_builder.public_key(private_key.public_key())
    cert_builder = cert_builder.serial_number(x509.random_serial_number())
    cert_builder = cert_builder.not_valid_before(datetime.datetime.utcnow())
    cert_builder = cert_builder.not_valid_after(datetime.datetime.utcnow() + datetime.timedelta(days=365))
    
    # Add extensions for better browser compatibility
    cert_builder = cert_builder.add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName("localhost"),
            x509.DNSName("127.0.0.1"),
            x509.DNSName("::1"),
            x509.IPAddress(ipaddress.IPv4Address("127.0.0.1")),
            x509.IPAddress(ipaddress.IPv6Address("::1")),
        ]),
        critical=False,
    )
    
    # Add key usage extensions
    cert_builder = cert_builder.add_extension(
        x509.KeyUsage(
            digital_signature=True,
            key_encipherment=True,
            key_agreement=False,
            key_cert_sign=False,
            crl_sign=False,
            content_commitment=False,
            data_encipherment=False,
            encipher_only=False,
            decipher_only=False,
        ),
        critical=True,
    )
    
    cert_builder = cert_builder.add_extension(
        x509.ExtendedKeyUsage([
            ExtendedKeyUsageOID.SERVER_AUTH,
        ]),
        critical=True,
    )
    
    # Sign certificate
    certificate = cert_builder.sign(private_key, hashes.SHA256())
    
    # Write private key
    with open("localhost_trusted.key", "wb") as f:
        f.write(private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    # Write certificate
    with open("localhost_trusted.crt", "wb") as f:
        f.write(certificate.public_bytes(serialization.Encoding.PEM))
    
    print("✅ Trusted SSL certificate created:")
    print("   📁 localhost_trusted.key (private key)")  
    print("   📁 localhost_trusted.crt (certificate)")
    print("   🏛️ Organization: Ministry of Statistics")
    print("   📅 Valid for: 1 year")
    print("   🌐 Domains: localhost, 127.0.0.1")
    
    return True

if __name__ == "__main__":
    create_trusted_certificate()