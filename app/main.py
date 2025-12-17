"""
FastAPI main application
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
from app.config import get_settings
from app.database import init_db
from app.api import auth, datasets, query, users, plfs, frontend

settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title="MoSPI Data Portal Infrastructure API",
    description="""
    ## Track: Data Dissemination - STATATHON 2025
    
    Create an API gateway to run SQL queries on Survey Datasets and retrieve 
    the results in user-friendly form like JSON.
    
    ### 🎯 Problem Statement Requirements Met:
    
    1. **Structured Database Ingestion** ✓
       - Load datasets into relational DB with preserved metadata
       - Real PLFS data: 1,472 records from microdata.gov.in
    
    2. **Configurable Query Framework** ✓
       - YAML-based configuration for dynamic query building
       - No hardcoded filters, metadata-driven queries
    
    3. **RESTful API Layer** ✓
       - 20+ endpoints with standard HTTP methods
       - JSON responses with proper error codes (400, 402, 429, 500)
    
    4. **Multi-dimensional Filtering** ✓
       - Query example: `state=Maharashtra&gender=female&age=15-29`
       - Support for complex parameter combinations
    
    5. **Access Control & Usage Metering** ✓
       - Rate-limiting: 100/1000/10000 requests per day by role
       - Volume caps: 10/100/1000 MB per day
       - Usage tracking and monitoring
    
    6. **Micro-Payment Feature** ✓
       - Simulated pricing model with credits system
       - Pay-per-use for premium access
       - Transaction history and billing
    
    7. **Developer Experience** ✓
       - OpenAPI/Swagger documentation (this page)
       - Interactive API testing
       - Comprehensive examples
    
    ### 📊 Available Datasets:
    
    * **District Codes**: 695 records (all India)
    * **Item Codes**: 377 survey items across 8 blocks
    * **Data Layout**: 400 structure definitions
    * **Source**: Periodic Labour Force Survey (PLFS)
    
    ### 🔐 Authentication:
    
    1. Register: `POST /api/v1/auth/register`
    2. Login: `POST /api/v1/auth/login` → Get JWT token
    3. Use token: `Authorization: Bearer <your_token>`
    
    ### 👥 User Roles:
    
    * **PUBLIC**: 100 requests/day, 10 MB/day, 1,000 credits
    * **RESEARCHER**: 1,000 requests/day, 100 MB/day
    * **PREMIUM**: 10,000 requests/day, 1,000 MB/day
    * **ADMIN**: Unlimited access
    
    ### 🔍 Example Multi-dimensional Query:
    
    ```
    GET /api/v1/query?state=Maharashtra&gender=female&age=15-29&limit=100
    GET /api/v1/plfs/district-codes?state=PUNJAB
    GET /api/v1/plfs/item-codes?block_no=3
    ```
    
    ### 🌐 Visit: [Landing Page](/) for visual interface
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add response time header to all requests"""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}"
    return response


# Include routers - Frontend first for landing page
app.include_router(frontend.router)  # Landing page at /
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(datasets.router, prefix=settings.API_V1_PREFIX)
app.include_router(query.router, prefix=settings.API_V1_PREFIX)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(plfs.router, prefix=settings.API_V1_PREFIX)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "MoSPI DPI",
        "version": "1.0.0"
    }


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request: Request, exc):
    """Handle 404 errors"""
    return JSONResponse(
        status_code=404,
        content={"detail": "Resource not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc):
    """Handle 500 errors"""
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
