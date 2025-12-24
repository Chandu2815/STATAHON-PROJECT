"""
Security middleware for FastAPI application
Implements security headers and HTTPS enforcement for Railway deployment
"""
from fastapi import Request
from fastapi.responses import RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
import os


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.
    Prevents Chrome "Dangerous site" warnings and improves security posture.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        # Detect production environment (Railway sets these)
        self.is_production = os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY_PROJECT_ID")
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Content Security Policy - Prevents XSS attacks
        # Allow same-origin content, inline scripts/styles (needed for templates), 
        # and trusted CDNs for images and scripts
        csp_directives = [
            "default-src 'self'",
            "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com",
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net https://cdnjs.cloudflare.com",
            "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net",
            "img-src 'self' data: https: blob:",
            "connect-src 'self' https:",
            "frame-ancestors 'self'",
            "form-action 'self'",
            "base-uri 'self'",
            "upgrade-insecure-requests" if self.is_production else ""
        ]
        csp_value = "; ".join([d for d in csp_directives if d])
        response.headers["Content-Security-Policy"] = csp_value
        
        # HTTP Strict Transport Security - Forces HTTPS for 1 year
        # Only set in production to avoid issues with local development
        if self.is_production:
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains; preload"
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        
        # XSS Protection (legacy but still useful)
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer Policy - Limit referrer information
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy - Restrict browser features
        response.headers["Permissions-Policy"] = (
            "accelerometer=(), camera=(), geolocation=(), gyroscope=(), "
            "magnetometer=(), microphone=(), payment=(), usb=()"
        )
        
        # Remove server header to avoid fingerprinting
        if "server" in response.headers:
            del response.headers["server"]
        
        return response


class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    """
    Middleware to redirect HTTP to HTTPS in production.
    Railway terminates SSL at the proxy level, so we check X-Forwarded-Proto header.
    """
    
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.is_production = os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY_PROJECT_ID")
    
    async def dispatch(self, request: Request, call_next):
        # Only redirect in production
        if self.is_production:
            # Railway/Cloud proxies set X-Forwarded-Proto header
            forwarded_proto = request.headers.get("x-forwarded-proto", "https")
            
            if forwarded_proto == "http":
                # Build HTTPS URL
                url = request.url
                https_url = url.replace(scheme="https")
                return RedirectResponse(url=str(https_url), status_code=301)
        
        return await call_next(request)


class TrustedHostMiddleware(BaseHTTPMiddleware):
    """
    Validates that requests come from trusted hosts.
    Prevents host header attacks.
    """
    
    def __init__(self, app: ASGIApp, allowed_hosts: list = None):
        super().__init__(app)
        self.allowed_hosts = allowed_hosts or ["*"]
        self.is_production = os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY_PROJECT_ID")
    
    async def dispatch(self, request: Request, call_next):
        if self.is_production and "*" not in self.allowed_hosts:
            host = request.headers.get("host", "").split(":")[0]
            if host not in self.allowed_hosts and not any(
                host.endswith(f".{allowed}") for allowed in self.allowed_hosts if allowed.startswith(".")
            ):
                from fastapi.responses import JSONResponse
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Invalid host header"}
                )
        
        return await call_next(request)
