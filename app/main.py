"""
FastAPI main application
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import time
from app.config import get_settings
from app.database import init_db
from app.api import auth, datasets, query, users, plfs

settings = get_settings()

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="""
    ## MoSPI Data Portal Infrastructure (DPI)
    
    A comprehensive Data Portal Infrastructure built for the Ministry of Statistics 
    and Programme Implementation (MoSPI) to enable efficient data access, querying, 
    and management of statistical datasets.
    
    ### Features
    
    * **Multi-dimensional Filtering**: Query data by state, gender, age group, and more
    * **Access Control**: Role-based access with rate limiting and usage metering
    * **Micro-Payment System**: Pay-per-use model with credits system
    * **RESTful API**: Comprehensive API endpoints for data access
    * **OpenAPI Documentation**: Interactive API documentation with Swagger UI
    
    ### Authentication
    
    Most endpoints require authentication. Use the `/auth/register` endpoint to create 
    an account and `/auth/login` to get an access token.
    
    ### User Roles
    
    * **Public**: 100 requests/day, 10 MB/day
    * **Researcher**: 1000 requests/day, 100 MB/day
    * **Premium**: 10000 requests/day, 1000 MB/day
    * **Admin**: Unlimited access
    
    ### Example Query
    
    ```
    GET /api/v1/query?dataset=census&state=Maharashtra&gender=female&age_group=15-29
    ```
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


# Include routers
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(datasets.router, prefix=settings.API_V1_PREFIX)
app.include_router(query.router, prefix=settings.API_V1_PREFIX)
app.include_router(users.router, prefix=settings.API_V1_PREFIX)
app.include_router(plfs.router, prefix=settings.API_V1_PREFIX)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup"""
    init_db()


@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Welcome to MoSPI Data Portal Infrastructure",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }


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
