from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import List, Dict, Any
import json
from db import get_db, engine, test_connection

# Initialize FastAPI app
app = FastAPI(
    title="Survey Data API",
    description="Production-ready API for managing survey data with PostgreSQL",
    version="2.0.0"
)


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


@app.get("/")
async def root():
    """
    Root endpoint to confirm API is running.
    """
    return {
        "message": "Survey Data API is running",
        "status": "online",
        "version": "2.0.0",
        "docs": "/docs"
    }


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
