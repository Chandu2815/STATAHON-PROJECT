"""
Frontend landing page for MoSPI Data Portal
"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path
from app.config import get_settings

router = APIRouter(tags=["Frontend"])

# Get templates directory
TEMPLATES_DIR = Path(__file__).parent.parent / "templates"


@router.get("/", response_class=HTMLResponse)
def home_page():
    """
    Landing page for MoSPI Data Portal
    """
    index_file = TEMPLATES_DIR / "index.html"
    if index_file.exists():
        with open(index_file, 'r', encoding='utf-8') as f:
            content = f.read()
            settings = get_settings()
            content = content.replace("__VITE_SURVEY_AI_URL__", settings.VITE_SURVEY_AI_URL)
            return content
    return "<h1>Home page not found</h1>"


@router.get("/home", response_class=HTMLResponse)
def home_page_alt():
    """
    Alternative route for landing page - redirect to /
    """
    return '<script>window.location.href="/";</script>'


@router.get("/login", response_class=HTMLResponse)
def login_page():
    """
    Login page for all users
    """
    login_file = TEMPLATES_DIR / "login.html"
    if login_file.exists():
        with open(login_file, 'r', encoding='utf-8') as f:
            content = f.read()
            settings = get_settings()
            content = content.replace("__VITE_SURVEY_AI_URL__", settings.VITE_SURVEY_AI_URL)
            return content
    return "<h1>Login page not found</h1>"


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard_page():
    """
    Dashboard for public and researcher users
    """
    dashboard_file = TEMPLATES_DIR / "dashboard.html"
    if dashboard_file.exists():
        with open(dashboard_file, 'r', encoding='utf-8') as f:
            content = f.read()
            settings = get_settings()
            content = content.replace("__VITE_SURVEY_AI_URL__", settings.VITE_SURVEY_AI_URL)
            content = content.replace("__VITE_APP_URL__", settings.VITE_APP_URL)
            return content
    return "<h1>Dashboard not found</h1>"


@router.get("/register", response_class=HTMLResponse)
def register_page():
    """
    Registration page for new users
    """
    register_file = TEMPLATES_DIR / "register.html"
    if register_file.exists():
        with open(register_file, 'r', encoding='utf-8') as f:
            content = f.read()
            settings = get_settings()
            content = content.replace("__VITE_SURVEY_AI_URL__", settings.VITE_SURVEY_AI_URL)
            return content
    return "<h1>Register page not found</h1>"


@router.get("/admin/login", response_class=HTMLResponse)
def admin_login_page():
    """
    Admin login page - separate from public portal
    """
    admin_login_file = TEMPLATES_DIR / "admin_login.html"
    if admin_login_file.exists():
        with open(admin_login_file, 'r', encoding='utf-8') as f:
            return f.read()
    return "<h1>Admin login page not found</h1>"


@router.get("/admin/dashboard", response_class=HTMLResponse)
def admin_dashboard_page():
    """
    Admin dashboard - requires admin authentication
    """
    admin_dashboard_file = TEMPLATES_DIR / "admin_dashboard.html"
    if admin_dashboard_file.exists():
        with open(admin_dashboard_file, 'r', encoding='utf-8') as f:
            return f.read()
    return "<h1>Admin dashboard not found</h1>"


@router.get("/upgrade", response_class=HTMLResponse)
def upgrade_page():
    """
    Premium upgrade page for users
    """
    upgrade_file = TEMPLATES_DIR / "upgrade.html"
    if upgrade_file.exists():
        with open(upgrade_file, 'r', encoding='utf-8') as f:
            return f.read()
    return "<h1>Upgrade page not found</h1>"


@router.get("/survey-ai", response_class=HTMLResponse)
def survey_ai_page():
    """
    Survey AI data collection form
    """
    survey_file = TEMPLATES_DIR / "survey.html"
    if survey_file.exists():
        with open(survey_file, 'r', encoding='utf-8') as f:
            return f.read()
    return "<h1>Survey page not found</h1>"


@router.get("/admin", response_class=HTMLResponse)
def admin_redirect():
    """
    Redirect /admin to /admin/login
    """
    return '<script>window.location.href="/admin/login";</script>'



@router.get("/logout", response_class=HTMLResponse)
def logout_endpoint():
    """
    Clear localStorage and redirect to login
    """
    return """
    <script>
        localStorage.removeItem('access_token');
        localStorage.removeItem('user_role');
        localStorage.removeItem('username');
        window.location.href='/login';
    </script>
    """
