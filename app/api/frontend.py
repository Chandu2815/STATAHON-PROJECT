"""
Frontend landing page for MoSPI Data Portal
"""
from fastapi import APIRouter
from fastapi.responses import HTMLResponse, FileResponse
from pathlib import Path

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
            return f.read()
    return "<h1>Home page not found</h1>"


@router.get("/home", response_class=HTMLResponse)
def home_page_alt():
    """
    Alternative route for landing page
    """
    index_file = TEMPLATES_DIR / "index.html"
    if index_file.exists():
        with open(index_file, 'r', encoding='utf-8') as f:
            return f.read()
    return "<h1>Home page not found</h1>"


@router.get("/login", response_class=HTMLResponse)
def login_page():
    """
    Login page for all users
    """
    login_file = TEMPLATES_DIR / "login.html"
    if login_file.exists():
        with open(login_file, 'r', encoding='utf-8') as f:
            return f.read()
    return "<h1>Login page not found</h1>"


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard_page():
    """
    Dashboard for public and researcher users
    """
    dashboard_file = TEMPLATES_DIR / "dashboard.html"
    if dashboard_file.exists():
        with open(dashboard_file, 'r', encoding='utf-8') as f:
            return f.read()
    return "<h1>Dashboard not found</h1>"


@router.get("/register", response_class=HTMLResponse)
def register_page():
    """
    Registration page for new users
    """
    register_file = TEMPLATES_DIR / "register.html"
    if register_file.exists():
        with open(register_file, 'r', encoding='utf-8') as f:
            return f.read()
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


@router.get("/admin", response_class=HTMLResponse)
def admin_redirect():
    """
    Redirect /admin to /admin/login
    """
    return '<script>window.location.href="/admin/login";</script>'


@router.get("/", response_class=HTMLResponse)
def landing_page():
    """
    Landing page - redirects to login page
    """
    return '<script>window.location.href="/login";</script>'


@router.get("/home", response_class=HTMLResponse)
def home_page():
    """
    Portal overview page (accessible from login page)
    """
    return """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MoSPI Data Portal Infrastructure</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                padding: 20px;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 20px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                overflow: hidden;
            }
            .header {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px;
                text-align: center;
            }
            .header h1 {
                font-size: 2.5em;
                margin-bottom: 10px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            }
            .header p {
                font-size: 1.2em;
                opacity: 0.95;
            }
            .content {
                padding: 40px;
            }
            .section {
                margin-bottom: 40px;
            }
            .section h2 {
                color: #667eea;
                margin-bottom: 20px;
                font-size: 1.8em;
                border-bottom: 3px solid #667eea;
                padding-bottom: 10px;
            }
            .feature-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-top: 20px;
            }
            .feature-card {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                transition: transform 0.3s, box-shadow 0.3s;
            }
            .feature-card:hover {
                transform: translateY(-5px);
                box-shadow: 0 8px 12px rgba(0,0,0,0.2);
            }
            .feature-card h3 {
                color: #667eea;
                margin-bottom: 10px;
                font-size: 1.3em;
            }
            .feature-card p {
                color: #555;
                line-height: 1.6;
            }
            .stats {
                display: flex;
                justify-content: space-around;
                flex-wrap: wrap;
                gap: 20px;
                margin: 30px 0;
            }
            .stat-box {
                background: #667eea;
                color: white;
                padding: 30px;
                border-radius: 15px;
                text-align: center;
                min-width: 200px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .stat-box .number {
                font-size: 2.5em;
                font-weight: bold;
                margin-bottom: 10px;
            }
            .stat-box .label {
                font-size: 1em;
                opacity: 0.9;
            }
            .cta-buttons {
                display: flex;
                gap: 20px;
                justify-content: center;
                flex-wrap: wrap;
                margin: 40px 0;
            }
            .btn {
                display: inline-block;
                padding: 15px 40px;
                border-radius: 50px;
                text-decoration: none;
                font-weight: bold;
                font-size: 1.1em;
                transition: all 0.3s;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            }
            .btn-primary {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .btn-primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 12px rgba(0,0,0,0.2);
            }
            .btn-secondary {
                background: white;
                color: #667eea;
                border: 2px solid #667eea;
            }
            .btn-secondary:hover {
                background: #667eea;
                color: white;
            }
            .requirements {
                background: #f8f9fa;
                padding: 30px;
                border-radius: 15px;
                margin: 30px 0;
            }
            .requirements ul {
                list-style: none;
                padding-left: 0;
            }
            .requirements li {
                padding: 12px 0;
                padding-left: 30px;
                position: relative;
                font-size: 1.1em;
            }
            .requirements li:before {
                content: "✓";
                position: absolute;
                left: 0;
                color: #667eea;
                font-weight: bold;
                font-size: 1.5em;
            }
            .example-query {
                background: #2d3748;
                color: #68d391;
                padding: 20px;
                border-radius: 10px;
                font-family: 'Courier New', monospace;
                margin: 20px 0;
                overflow-x: auto;
            }
            .footer {
                background: #2d3748;
                color: white;
                text-align: center;
                padding: 30px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🏛️ MoSPI Data Portal Infrastructure</h1>
                <p>Ministry of Statistics and Programme Implementation</p>
                <p style="font-size: 0.9em; margin-top: 10px;">API Gateway for Survey Datasets with Advanced Query Capabilities</p>
            </div>
            
            <div class="content">
                <!-- Statistics -->
                <div class="stats">
                    <div class="stat-box">
                        <div class="number">517K+</div>
                        <div class="label">Survey Records</div>
                    </div>
                    <div class="stat-box">
                        <div class="number">102K</div>
                        <div class="label">Households</div>
                    </div>
                    <div class="stat-box">
                        <div class="number">415K</div>
                        <div class="label">Individuals</div>
                    </div>
                    <div class="stat-box">
                        <div class="number">25+</div>
                        <div class="label">API Endpoints</div>
                    </div>
                </div>

                <!-- CTA Buttons -->
                <div class="cta-buttons">
                    <a href="/login" class="btn btn-primary">🔐 Login / Access Portal</a>
                    <a href="/docs" class="btn btn-secondary">📖 API Documentation</a>
                </div>

                <!-- Track Information -->
                <div class="section">
                    <h2>📊 Track: Data Dissemination</h2>
                    <p style="font-size: 1.1em; line-height: 1.8; color: #555;">
                        This API gateway enables efficient querying of Survey Datasets and retrieves results 
                        in user-friendly formats like JSON. Built for researchers, policymakers, and data 
                        analysts to access comprehensive micro-data from government surveys.
                    </p>
                </div>

                <!-- Key Features -->
                <div class="section">
                    <h2>✨ Key Features</h2>
                    <div class="feature-grid">
                        <div class="feature-card">
                            <h3>🗄️ Structured Database</h3>
                            <p>Load datasets into relational database with preserved metadata and relationships</p>
                        </div>
                        <div class="feature-card">
                            <h3>⚙️ Configurable Queries</h3>
                            <p>YAML-based configuration for dynamic query building without hardcoded filters</p>
                        </div>
                        <div class="feature-card">
                            <h3>🌐 RESTful API</h3>
                            <p>Standard HTTP methods with JSON responses and proper error codes</p>
                        </div>
                        <div class="feature-card">
                            <h3>🔍 Multi-dimensional Filtering</h3>
                            <p>Query with multiple parameters: state, gender, age groups, and more</p>
                        </div>
                        <div class="feature-card">
                            <h3>🔐 Access Control</h3>
                            <p>Role-based access with rate-limiting and usage metering</p>
                        </div>
                        <div class="feature-card">
                            <h3>💳 Micro-Payment System</h3>
                            <p>Credit-based billing for premium access and pay-per-use queries</p>
                        </div>
                    </div>
                </div>

                <!-- Example Query -->
                <div class="section">
                    <h2>🔍 Example Multi-dimensional Queries</h2>
                    <p style="margin-bottom: 15px;"><strong>Household Survey - Filter by location and demographics:</strong></p>
                    <div class="example-query">
GET /api/query/household_survey?filters={"State_Ut_Code": 28, "Sector": 1, "Social_Group": 2}
# Rural households from SC social group in Karnataka
                    </div>
                    <p style="margin-top: 20px; margin-bottom: 15px;"><strong>Person Survey - Filter by employment and demographics:</strong></p>
                    <div class="example-query">
GET /api/query/person_survey?filters={"Age": {"$gte": 25, "$lte": 35}, "Sex": 1, "Sector": 2}
# Urban males aged 25-35
                    </div>
                    <p style="margin-top: 15px; color: #555;">
                        Query datasets by state, district, gender, age, employment status, education level, and more. 
                        Supports complex filtering with operators like $gte, $lte, $in. Results returned in JSON with pagination.
                    </p>
                </div>

                <!-- Requirements Met -->
                <div class="section">
                    <h2>✅ Problem Statement Requirements</h2>
                    <div class="requirements">
                        <ul>
                            <li><strong>Structured Database Ingestion:</strong> Real PLFS data loaded with metadata preservation</li>
                            <li><strong>Configurable Query Framework:</strong> YAML configs define structure and filters</li>
                            <li><strong>RESTful API Layer:</strong> 20+ endpoints with standard HTTP methods</li>
                            <li><strong>Multi-dimensional Filtering:</strong> Support for complex query parameters</li>
                            <li><strong>Access Control & Usage Metering:</strong> Rate limits, volume caps, usage tracking</li>
                            <li><strong>Micro-Payment Integration:</strong> Credit system with pricing tiers</li>
                            <li><strong>Developer Experience:</strong> OpenAPI/Swagger documentation with examples</li>
                        </ul>
                    </div>
                </div>

                <!-- User Roles -->
                <div class="section">
                    <h2>👥 User Roles & Access Tiers</h2>
                    <div class="feature-grid">
                        <div class="feature-card">
                            <h3>🆓 PUBLIC</h3>
                            <p><strong>100 requests/day</strong></p>
                            <p>10 MB data limit</p>
                            <p>1,000 initial credits</p>
                        </div>
                        <div class="feature-card">
                            <h3>🔬 RESEARCHER</h3>
                            <p><strong>1,000 requests/day</strong></p>
                            <p>100 MB data limit</p>
                            <p>Data export capabilities</p>
                        </div>
                        <div class="feature-card">
                            <h3>⭐ PREMIUM</h3>
                            <p><strong>10,000 requests/day</strong></p>
                            <p>1,000 MB data limit</p>
                            <p>Advanced analytics & priority support</p>
                        </div>
                        <div class="feature-card">
                            <h3>👑 ADMIN</h3>
                            <p><strong>Unlimited access</strong></p>
                            <p>Full system control</p>
                            <p>Administrative tools</p>
                        </div>
                    </div>
                </div>

                <!-- Quick Start -->
                <div class="section">
                    <h2>🚀 Quick Start</h2>
                    <ol style="font-size: 1.1em; line-height: 2; color: #555; padding-left: 30px;">
                        <li>Register at <a href="/docs#/Authentication/register_user_api_v1_auth_register_post" style="color: #667eea; font-weight: bold;">/api/v1/auth/register</a></li>
                        <li>Login to receive JWT token</li>
                        <li>Use token in Authorization header: <code>Bearer &lt;token&gt;</code></li>
                        <li>Start querying datasets through API endpoints</li>
                    </ol>
                </div>

                <!-- Available Datasets -->
                <div class="section">
                    <h2>📁 Available Datasets</h2>
                    <div class="feature-grid">
                        <div class="feature-card" style="background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);">
                            <h3>🏠 Household Survey (CHHV1)</h3>
                            <p><strong>~102,000 households</strong> | 38 fields</p>
                            <p>Demographics, expenditure, social groups, consumption patterns</p>
                            <p style="margin-top: 10px;"><strong>Filters:</strong> State, District, Sector, Quarter, Religion, Social Group</p>
                            <p><a href="/docs#/Datasets" style="color: #667eea; font-weight: bold;">View API →</a></p>
                        </div>
                        <div class="feature-card" style="background: linear-gradient(135deg, #a1c4fd 0%, #c2e9fb 100%);">
                            <h3>👥 Person Survey (CPERV1)</h3>
                            <p><strong>~415,000 individuals</strong> | 140 fields</p>
                            <p>Employment status, education, earnings, daily activities</p>
                            <p style="margin-top: 10px;"><strong>Filters:</strong> Age, Sex, Education, Employment Status, Industry, Occupation</p>
                            <p><a href="/docs#/Datasets" style="color: #667eea; font-weight: bold;">View API →</a></p>
                        </div>
                        <div class="feature-card">
                            <h3>📍 District Codes</h3>
                            <p>695 records covering all India districts with NSS codes</p>
                            <p><a href="/api/v1/plfs/district-codes" style="color: #667eea;">View Endpoint →</a></p>
                        </div>
                        <div class="feature-card">
                            <h3>📋 Item Codes</h3>
                            <p>377 survey items across 8 PLFS blocks</p>
                            <p><a href="/api/v1/plfs/item-codes" style="color: #667eea;">View Endpoint →</a></p>
                        </div>
                        <div class="feature-card">
                            <h3>🗂️ Data Layout</h3>
                            <p>400 structure records defining data organization</p>
                            <p><a href="/api/v1/plfs/data-layout" style="color: #667eea;">View Endpoint →</a></p>
                        </div>
                    </div>
                </div>

                <!-- Technology Stack -->
                <div class="section">
                    <h2>🛠️ Technology Stack</h2>
                    <div style="background: #f8f9fa; padding: 25px; border-radius: 15px;">
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                            <div><strong>Framework:</strong> FastAPI 0.104.1</div>
                            <div><strong>Database:</strong> SQLite + SQLAlchemy</div>
                            <div><strong>Authentication:</strong> JWT (python-jose)</div>
                            <div><strong>Security:</strong> bcrypt 4.0.1</div>
                            <div><strong>Data Processing:</strong> pandas, openpyxl</div>
                            <div><strong>Server:</strong> uvicorn</div>
                        </div>
                    </div>
                </div>

                <!-- Impact -->
                <div class="section">
                    <h2>🌟 Impact & Outcomes</h2>
                    <div class="requirements">
                        <ul>
                            <li><strong>Time-to-insight reduced:</strong> Fast queries with pagination and filtering</li>
                            <li><strong>Equitable access:</strong> Free tier for researchers and students</li>
                            <li><strong>Privacy-compliant:</strong> Role-based access control and audit logs</li>
                            <li><strong>Scalable architecture:</strong> Reusable for other government datasets</li>
                            <li><strong>Developer-friendly:</strong> Comprehensive API documentation</li>
                        </ul>
                    </div>
                </div>
            </div>

            <div class="footer">
                <p style="font-size: 1.2em; margin-bottom: 10px;">
                    <strong>MoSPI Data Portal Infrastructure</strong>
                </p>
                <p style="opacity: 0.8;">
                    Built for STATATHON 2025 | Track: Data Dissemination
                </p>
                <p style="margin-top: 15px;">
                    📧 support@mospi.gov.in | 🔗 <a href="/docs" style="color: white;">API Docs</a> | 
                    🌐 <a href="https://microdata.gov.in" style="color: white;">microdata.gov.in</a>
                </p>
            </div>
        </div>
    </body>
    </html>
    """
