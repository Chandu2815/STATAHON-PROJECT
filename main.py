"""
Root application entry point - imports the full app from app/main.py
This file simply re-exports the app from app.main which contains:
- Frontend routes: /, /login, /register, /dashboard, /admin, etc.
- API endpoints: /api/v1/auth/*, /api/v1/datasets/*, /api/v1/query/*, etc.
- Static files: /static/*
"""
from app.main import app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
