# Skill: Python FastAPI Development
# Survey-AI Dataset Explorer System

## Scope
This skill applies to Python FastAPI backend development (Port 8001) for the Survey-AI project.

## Core Concepts

### Architecture Pattern
```
APIRouter (routes) → Service Layer → Pydantic Schemas → SQLAlchemy/psycopg2 → PostgreSQL
```

### Key Rules

1. **APIRouter for Modular Routes**
   - Each feature gets its own router file
   - Use APIRouter with prefix and tags
   - Mount routers to app with include_router

   ```python
   from fastapi import APIRouter
   
   router = APIRouter(prefix="/datasets", tags=["datasets"])
   
   @router.get("/hierarchical")
   async def get_hierarchical_datasets():
       pass
   
   # In main.py
   app.include_router(router)
   ```

2. **Async Endpoints Mandatory**
   - All endpoint functions must be `async def`
   - Use `await` for database operations
   - Never use synchronous operations in async context

   ```python
   @router.get("/datasets/{dataset_id}")
   async def get_dataset(dataset_id: str, db = Depends(get_db)):
       # Correct: async call
       dataset = await db.query(...).first()
       return dataset
   ```

3. **Dependency Injection for Database**
   - Use `Depends(get_db)` pattern
   - Never create database connections in endpoints
   - Session management handled by dependency

   ```python
   from sqlalchemy.orm import Session
   from database.connection import get_db
   
   async def get_db():
       db = SessionLocal()
       try:
           yield db
       finally:
           db.close()
   
   @router.get("/datasets")
   async def list_datasets(db: Session = Depends(get_db)):
       return db.query(Dataset).all()
   ```

4. **Pydantic Schemas for Validation**
   - Define request/response schemas with Pydantic
   - Use for automatic validation and documentation
   - Leverage type hints for OpenAPI

   ```python
   from pydantic import BaseModel
   from typing import List, Optional
   
   class DatasetSchema(BaseModel):
       id: str
       name: str
       category: str
       records: int
       columns: List[str]
       
       class Config:
           from_attributes = True
   
   @router.get("/datasets/{dataset_id}", response_model=DatasetSchema)
   async def get_dataset(dataset_id: str, db: Session = Depends(get_db)):
       dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
       return dataset
   ```

5. **Parameterized Queries Only**
   - Use SQLAlchemy ORM whenever possible
   - If raw SQL, use parameterized queries
   - Never concatenate user input

   ```python
   # ✅ PREFERRED: SQLAlchemy ORM
   user = db.query(User).filter(User.email == email).first()
   
   # ✅ ACCEPTABLE: Parameterized raw SQL
   from sqlalchemy import text
   result = db.execute(
       text("SELECT * FROM users WHERE email = :email"),
       {"email": email}
   )
   
   # ❌ NEVER: String concatenation
   result = db.execute(f"SELECT * FROM users WHERE email = '{email}'")
   ```

6. **HTTPException for Error Handling**
   - Use HTTPException for known errors
   - Implement centralized exception handlers
   - Return consistent error format

   ```python
   from fastapi import HTTPException
   
   @router.get("/datasets/{dataset_id}")
   async def get_dataset(dataset_id: str, db: Session = Depends(get_db)):
       dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
       
       if not dataset:
           raise HTTPException(
               status_code=404,
               detail="Dataset not found"
           )
       
       return dataset
   
   # Exception handler
   @app.exception_handler(HTTPException)
   async def http_exception_handler(request, exc):
       return {
           "success": False,
           "error": exc.detail,
           "code": "HTTP_ERROR",
           "meta": {"statusCode": exc.status_code}
       }
   ```

7. **Response Format Consistency**
   - All responses: `{ success: true/false, data: {...}, meta: {...} }`
   - Use response models for documentation
   - Include metadata for tracking

   ```python
   from pydantic import BaseModel
   from typing import Generic, TypeVar
   
   T = TypeVar('T')
   
   class ResponseModel(BaseModel, Generic[T]):
       success: bool
       data: T
       meta: dict = {}
   
   class ErrorResponse(BaseModel):
       success: bool = False
       error: str
       code: str
       meta: dict = {}
   
   @router.get("/datasets")
   async def list_datasets(db: Session = Depends(get_db)):
       datasets = db.query(Dataset).all()
       return {
           "success": True,
           "data": datasets,
           "meta": {"count": len(datasets)}
       }
   ```

8. **Service Layer for Business Logic**
   - Keep routers thin and focused
   - Move logic to service classes
   - Services handle database access

   ```python
   # services/dataset_service.py
   class DatasetService:
       def __init__(self, db: Session):
           self.db = db
       
       async def get_hierarchical_datasets(self):
           """Fetch and organize datasets by category"""
           tables = self.db.execute(
               text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
           ).fetchall()
           
           hierarchical = {"HCES": [], "PLFS": [], "Survey": [], "Other": []}
           
           for table in tables:
               if table[0].startswith("hces_"):
                   hierarchical["HCES"].append(table[0])
               # ... categorize others
           
           return hierarchical
   
   # routers/datasets.py
   @router.get("/hierarchical")
   async def get_datasets_hierarchical(db: Session = Depends(get_db)):
       service = DatasetService(db)
       data = await service.get_hierarchical_datasets()
       return {"success": True, "data": data}
   ```

## Code Generation Checklist

- [ ] Use APIRouter with prefix and tags
- [ ] Make all endpoint functions async
- [ ] Use Depends(get_db) for database access
- [ ] Define Pydantic schemas for requests/responses
- [ ] Use SQLAlchemy ORM or parameterized queries
- [ ] Raise HTTPException for errors
- [ ] Return consistent response format
- [ ] Add docstrings to endpoints
- [ ] Validate input with Pydantic
- [ ] Include proper error handling
- [ ] Add response_model for auto-documentation

## Common Patterns

### Hierarchical Dataset Endpoint
```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from database.connection import get_db
from pydantic import BaseModel

router = APIRouter(prefix="/datasets", tags=["datasets"])

class DatasetItem(BaseModel):
    name: str
    label: str
    records: int

class HierarchicalResponse(BaseModel):
    HCES: list[DatasetItem]
    PLFS: list[DatasetItem]
    Survey: list[DatasetItem]
    Other: list[DatasetItem]

@router.get("/hierarchical")
async def get_datasets_hierarchical(db: Session = Depends(get_db)):
    """
    Get all datasets organized in hierarchical categories.
    
    Returns:
        Hierarchical structure with HCES, PLFS, Survey, and Other categories
    """
    try:
        result = db.execute(
            text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
        )
        tables = [row[0] for row in result.fetchall()]
        
        hierarchical = {
            "HCES": [],
            "PLFS": [],
            "Survey": [],
            "Other": []
        }
        
        for table in tables:
            if table.startswith("hces_"):
                hierarchical["HCES"].append({
                    "name": table,
                    "label": table.replace("_", " ").title(),
                    "records": 261000  # Get actual count
                })
            # ... categorize others
        
        return {
            "success": True,
            "data": hierarchical,
            "meta": {"timestamp": datetime.now().isoformat()}
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching datasets: {str(e)}"
        )
```

### Protected Endpoint with JWT
```python
from fastapi import Security, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthCredentials
import jwt

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthCredentials = Security(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, "secret_key", algorithms=["HS256"])
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication credentials"
        )

@router.get("/datasets/admin")
async def admin_datasets(current_user = Depends(verify_token)):
    """Admin-only endpoint requiring valid JWT"""
    return {"success": True, "data": [...]}
```

### Pagination Pattern
```python
from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar('T')

class PaginatedResponse(BaseModel, Generic[T]):
    success: bool
    data: list[T]
    meta: dict

@router.get("/datasets")
async def list_datasets(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """List datasets with pagination"""
    total = db.query(Dataset).count()
    datasets = db.query(Dataset).offset(skip).limit(limit).all()
    
    return {
        "success": True,
        "data": datasets,
        "meta": {
            "total": total,
            "skip": skip,
            "limit": limit,
            "hasMore": (skip + limit) < total
        }
    }
```

## When to Activate This Skill
- Creating new FastAPI endpoints
- Implementing dataset service features
- Writing database queries with SQLAlchemy
- Adding authentication to routes
- Creating response schemas
- Implementing error handling
- Optimizing database queries

## Related Skills
- database-expert (for SQL optimization)
- api-designer (for REST design patterns)
- debugging-assistant (for troubleshooting)

## FastAPI Resources
- Dependency Injection: Use for session management
- Pydantic: Use for request/response validation
- SQLAlchemy: Use for ORM-based queries
- HTTPException: Use for error responses
- APIRouter: Use for modular routing
