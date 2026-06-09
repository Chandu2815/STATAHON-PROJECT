from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import List, Dict, Any
from pathlib import Path
import json
from db import get_db, engine, test_connection

# Get the base directory
BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "app" / "templates"
STATIC_DIR = BASE_DIR / "app" / "static"

# Initialize FastAPI app
app = FastAPI(
    title="Survey Data API",
    description="Production-ready API for managing survey data with PostgreSQL",
    version="2.0.0"
)

# Mount static files
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# Pydantic models for request/response
class SurveyDataRequest(BaseModel):
    """Model for incoming survey data"""
    data: Dict[str, Any]


class SurveyDataResponse(BaseModel):
    """Model for survey data response"""
    id: int
    data: Dict[str, Any]
    created_at: str


@app.on_event("startup")
async def startup_event():
    """
    Initialize database on application startup.
    Verify connection pool is working.
    """
    result = test_connection()
    if result["status"] == "success":
        print("✓ Database connection verified at startup")
    else:
        print(f"✗ Database connection failed: {result['message']}")


@app.get("/", response_class=HTMLResponse)
async def root():
    """
    Serve the existing landing page from app/templates/index.html
    """
    index_file = TEMPLATES_DIR / "index.html"
    if index_file.exists():
        with open(index_file, 'r', encoding='utf-8') as f:
            return f.read()
    else:
        # Fallback to simple page if index.html doesn't exist
        return """
        <!DOCTYPE html>
        <html>
        <head>
            <title>STATAHON - Survey Data Portal</title>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
        </head>
        <body>
            <h1>STATAHON Survey Data Portal</h1>
            <p>Welcome! Visit <a href="/docs">API Documentation</a></p>
        </body>
        </html>
        """
            
            .header-buttons {
                display: flex;
                gap: 15px;
            }
            
            .btn-header {
                padding: 10px 25px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-weight: 600;
                text-decoration: none;
                transition: all 0.3s ease;
                font-size: 0.95em;
            }
            
            .btn-login {
                background: #1a3a5c;
                color: white;
            }
            
            .btn-login:hover {
                background: #0f2847;
            }
            
            .btn-register {
                background: #ff8a3d;
                color: white;
            }
            
            .btn-register:hover {
                background: #e67e2f;
            }
            
            /* Hero Section */
            .hero {
                background: linear-gradient(135deg, #3d5a7f 0%, #2c4563 50%, #1a8e8a 100%);
                padding: 80px 20px;
                position: relative;
                overflow: hidden;
            }
            
            .hero::after {
                content: '';
                position: absolute;
                bottom: -50px;
                left: 0;
                width: 100%;
                height: 120px;
                background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 120" preserveAspectRatio="none"><path d="M0,50 Q250,100 500,50 T1000,50 L1200,120 L0,120 Z" fill="white"></path></svg>');
                background-repeat: no-repeat;
                background-size: cover;
            }
            
            .hero-content {
                max-width: 800px;
                margin: 0 auto;
                text-align: center;
                color: white;
                position: relative;
                z-index: 10;
            }
            
            .hero h1 {
                font-size: 3.5em;
                margin-bottom: 20px;
                font-weight: 700;
                line-height: 1.2;
            }
            
            .hero p {
                font-size: 1.2em;
                margin-bottom: 40px;
                opacity: 0.95;
                line-height: 1.6;
            }
            
            .hero .btn {
                background: #ff8a3d;
                color: white;
                padding: 15px 50px;
                border: none;
                border-radius: 4px;
                font-size: 1.1em;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-block;
            }
            
            .hero .btn:hover {
                background: #e67e2f;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
            
            /* Content Section after hero */
            .content-section {
                background: white;
                padding: 80px 20px;
                margin-top: 50px;
            }
            
            .section-container {
                max-width: 1200px;
                margin: 0 auto;
            }
            
            .section-title {
                font-size: 2.2em;
                color: #1a3a5c;
                text-align: center;
                margin-bottom: 60px;
                font-weight: 700;
            }
            
            /* Platform Statistics */
            .stats-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 30px;
                margin-bottom: 60px;
            }
            
            .stat-card {
                text-align: center;
                padding: 30px;
                background: #f9f9f9;
                border-radius: 6px;
                border-top: 4px solid #ff8a3d;
            }
            
            .stat-number {
                font-size: 2.8em;
                color: #1a3a5c;
                font-weight: 700;
                margin-bottom: 10px;
            }
            
            .stat-label {
                color: #666;
                font-size: 1.1em;
                font-weight: 500;
            }
            
            /* Features Grid */
            .features-grid {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 30px;
                margin-top: 40px;
            }
            
            .feature-card {
                background: white;
                padding: 30px;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                transition: all 0.3s ease;
            }
            
            .feature-card:hover {
                box-shadow: 0 8px 20px rgba(0,0,0,0.1);
                transform: translateY(-3px);
            }
            
            .feature-icon {
                font-size: 2.5em;
                margin-bottom: 15px;
            }
            
            .feature-card h3 {
                color: #1a3a5c;
                margin-bottom: 10px;
                font-size: 1.3em;
            }
            
            .feature-card p {
                color: #666;
                line-height: 1.6;
            }
            
            /* Footer */
            footer {
                background: #1a3a5c;
                color: white;
                padding: 40px 20px;
                text-align: center;
                margin-top: 80px;
            }
            
            footer p {
                margin: 5px 0;
                opacity: 0.9;
            }
            
            .footer-links {
                margin-top: 15px;
                display: flex;
                justify-content: center;
                gap: 30px;
                flex-wrap: wrap;
            }
            
            .footer-links a {
                color: #ff8a3d;
                text-decoration: none;
                font-weight: 500;
            }
            
            .footer-links a:hover {
                text-decoration: underline;
            }
            
            @media (max-width: 768px) {
                .hero h1 {
                    font-size: 2em;
                }
                
                .hero p {
                    font-size: 1em;
                }
                
                .header-buttons {
                    gap: 10px;
                }
                
                .btn-header {
                    padding: 8px 15px;
                    font-size: 0.85em;
                }
                
                .section-title {
                    font-size: 1.8em;
                }
                
                .hero {
                    padding: 50px 15px;
                }
            }
        </style>
    </head>
    <body>
        <!-- Header -->
        <header>
            <div class="header-container">
                <a href="/" class="logo">
                    📊 STATAHON
                    <span class="logo-subtitle">Survey Data Portal</span>
                </a>
                <div class="header-buttons">
                    <button class="btn-header btn-login">Login</button>
                    <button class="btn-header btn-register">Register</button>
                </div>
            </div>
        </header>
        
        <!-- Hero Section -->
        <section class="hero">
            <div class="hero-content">
                <h1>Empowering India with Data</h1>
                <p>Access comprehensive statistical data and insights from our official data infrastructure platform. Unlock powerful analytics for informed decision-making.</p>
                <a href="/docs" class="btn">Get Started</a>
            </div>
        </section>
        
        <!-- Platform Statistics -->
        <section class="content-section">
            <div class="section-container">
                <h2 class="section-title">Platform Statistics</h2>
                
                <div class="stats-grid">
                    <div class="stat-card">
                        <div class="stat-number" id="total-records">Loading...</div>
                        <div class="stat-label">Active Records</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number">2.0.0</div>
                        <div class="stat-label">API Version</div>
                    </div>
                    <div class="stat-card">
                        <div class="stat-number" id="db-status-stat">Checking...</div>
                        <div class="stat-label">Database Status</div>
                    </div>
                </div>
                
                <h2 class="section-title" style="margin-top: 60px;">Core Features</h2>
                
                <div class="features-grid">
                    <div class="feature-card">
                        <div class="feature-icon">⚡</div>
                        <h3>High Performance</h3>
                        <p>Built with FastAPI for blazing-fast data access and real-time analytics processing.</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🗄️</div>
                        <h3>Robust Storage</h3>
                        <p>Enterprise-grade PostgreSQL database with secure data storage and ACID compliance.</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">📊</div>
                        <h3>Data Management</h3>
                        <p>Powerful tools for importing, organizing, and managing large datasets efficiently.</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">📈</div>
                        <h3>Analytics Ready</h3>
                        <p>Pre-optimized schema and indexing for fast analytical queries on your data.</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">🔒</div>
                        <h3>Security First</h3>
                        <p>Built with security best practices, parameterized queries, and connection pooling.</p>
                    </div>
                    <div class="feature-card">
                        <div class="feature-icon">📚</div>
                        <h3>API Documentation</h3>
                        <p>Interactive API docs, full OpenAPI specifications, and comprehensive examples.</p>
                    </div>
                </div>
            </div>
        </section>
        
        <!-- Footer -->
        <footer>
            <p><strong>STATAHON - Survey Data Portal</strong></p>
            <p>Official Data Infrastructure Platform</p>
            <div class="footer-links">
                <a href="/docs">API Docs</a>
                <a href="/redoc">ReDoc</a>
                <a href="/health">Health Check</a>
                <a href="https://github.com/Chandu2815/STATAHON-PROJECT" target="_blank">GitHub</a>
            </div>
            <p style="margin-top: 20px; opacity: 0.7; font-size: 0.9em;">v2.0.0 | Built with FastAPI & PostgreSQL | © 2026</p>
        </footer>
        
        <script>
            // Load live statistics
            async function loadStats() {
                try {
                    const response = await fetch('/data');
                    if (response.ok) {
                        const data = await response.json();
                        const count = data.length.toLocaleString();
                        document.getElementById('total-records').textContent = count;
                    }
                } catch (error) {
                    console.error('Failed to load records:', error);
                    document.getElementById('total-records').textContent = '—';
                }
                
                try {
                    const healthResponse = await fetch('/health');
                    if (healthResponse.ok) {
                        document.getElementById('db-status-stat').textContent = '✓ Active';
                        document.getElementById('db-status-stat').style.color = '#27ae60';
                    } else {
                        document.getElementById('db-status-stat').textContent = '⚠ Offline';
                        document.getElementById('db-status-stat').style.color = '#e74c3c';
                    }
                } catch (error) {
                    document.getElementById('db-status-stat').textContent = '✗ Error';
                    document.getElementById('db-status-stat').style.color = '#e74c3c';
                }
            }
            
            // Load stats when page loads
            window.addEventListener('load', loadStats);
        </script>
    </body>
    </html>
    """


@app.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint to verify API and database connectivity.
    """
    try:
        # Test database connection with a simple query
        db.execute(text("SELECT 1"))
        return {
            "status": "healthy",
            "database": "connected",
            "api": "running"
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Database unavailable: {str(e)}"
        )


@app.post("/add", status_code=status.HTTP_201_CREATED)
async def add_survey_data(
    request: SurveyDataRequest,
    db: Session = Depends(get_db)
):
    """
    Add new survey data to the database.
    
    Args:
        request: SurveyDataRequest containing the survey data
        db: Database session (injected via dependency)
    
    Returns:
        Success message with inserted data ID and timestamp
    """
    try:
        # Convert data dict to JSON string for JSONB column
        data_json = json.dumps(request.data)
        
        # Insert into survey_data table using parameterized query
        insert_query = text("""
            INSERT INTO survey_data (data)
            VALUES (:data)
            RETURNING id, created_at;
        """)
        
        result = db.execute(insert_query, {"data": data_json})
        row = result.fetchone()
        
        # Commit the transaction
        db.commit()
        
        if row:
            return {
                "message": "Survey data inserted successfully",
                "status": "created",
                "id": row[0],
                "created_at": row[1].isoformat() if row[1] else None,
                "data": request.data
            }
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to insert data into database"
            )
    
    except json.JSONDecodeError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JSON data: {str(e)}"
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@app.get("/data", response_model=List[SurveyDataResponse])
async def get_all_survey_data(db: Session = Depends(get_db)):
    """
    Fetch all records from the survey_data table.
    
    Args:
        db: Database session (injected via dependency)
    
    Returns:
        List of survey data records with id, data, and created_at
    """
    try:
        # Fetch all records from survey_data table
        select_query = text("""
            SELECT id, data, created_at
            FROM survey_data
            ORDER BY created_at DESC;
        """)
        
        result = db.execute(select_query)
        rows = result.fetchall()
        
        # Convert rows to list of dictionaries
        results = []
        for row in rows:
            results.append({
                "id": row[0],
                "data": json.loads(row[1]) if row[1] else {},
                "created_at": row[2].isoformat() if row[2] else None
            })
        
        return results
    
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error parsing stored JSON data: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@app.get("/data/{record_id}", response_model=SurveyDataResponse)
async def get_survey_data_by_id(
    record_id: int,
    db: Session = Depends(get_db)
):
    """
    Fetch a specific survey record by ID.
    
    Args:
        record_id: The ID of the survey record
        db: Database session (injected via dependency)
    
    Returns:
        Single survey data record with id, data, and created_at
    """
    try:
        select_query = text("""
            SELECT id, data, created_at
            FROM survey_data
            WHERE id = :record_id;
        """)
        
        result = db.execute(select_query, {"record_id": record_id})
        row = result.fetchone()
        
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Survey record with id {record_id} not found"
            )
        
        return {
            "id": row[0],
            "data": json.loads(row[1]) if row[1] else {},
            "created_at": row[2].isoformat() if row[2] else None
        }
    
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error parsing stored JSON data: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )


@app.get("/status/db")
async def database_status():
    """
    Get detailed database connection status.
    """
    return test_connection()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
