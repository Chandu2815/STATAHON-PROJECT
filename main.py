"""
Root application entry point - imports the full app from app/main.py
This file simply re-exports the app from app.main which contains:
- Frontend routes: /, /login, /register, /dashboard, /admin, etc.
- API endpoints: /api/v1/auth/*, /api/v1/datasets/*, /api/v1/query/*, etc.
- Static files: /static/*
"""
import os
import socket

from app.main import app


def _is_port_available(host: str, port: int) -> bool:
    bind_host = "" if host in {"0.0.0.0", "::"} else host
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        try:
            sock.bind((bind_host, port))
        except OSError:
            return False
    return True


def _resolve_server_config() -> tuple[str, int]:
    host = os.getenv("APP_HOST", os.getenv("HOST", "0.0.0.0"))
    explicit_port = os.getenv("APP_PORT") or os.getenv("PORT")
    port = int(explicit_port or "8000")

    if explicit_port:
        return host, port

    while not _is_port_available(host, port):
        print(f"[SERVER] Port {port} is already in use; trying {port + 1}")
        port += 1

    return host, port


if __name__ == "__main__":
    import uvicorn

    server_host, server_port = _resolve_server_config()
    print(f"[SERVER] Starting on http://{server_host}:{server_port}")
    uvicorn.run(
        app,
        host=server_host,
        port=server_port,
        log_level="info"
    )
