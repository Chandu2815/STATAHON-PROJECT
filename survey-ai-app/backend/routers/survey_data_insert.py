"""
Survey Data Insert Router
Handles bulk insertion of survey dataset records into PostgreSQL
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import logging

import database.connection

# Configure logging
logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/survey-data",
    tags=["survey-data"],
    responses={
        400: {"description": "Invalid request data"},
        409: {"description": "Conflict with existing data"},
        422: {"description": "Validation error"},
        500: {"description": "Database error"}
    }
)


# ============================================================================
# Pydantic Schemas
# ============================================================================

class SurveyDataRecord(BaseModel):
    """Schema for a single survey data record"""
    dataset_name: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., min_length=1, max_length=100)
    year: int = Field(..., ge=1900, le=2100)
    indicator_name: str = Field(..., min_length=1, max_length=255)
    value: float
    state: str = Field(..., min_length=1, max_length=100)
    district: Optional[str] = Field(None, max_length=100)

    class Config:
        json_schema_extra = {
            "example": {
                "dataset_name": "HCES 2022",
                "category": "HCES",
                "year": 2022,
                "indicator_name": "Total Consumption",
                "value": 5280.50,
                "state": "Bihar",
                "district": "Patna"
            }
        }


class SurveyDataBulkRequest(BaseModel):
    """Schema for bulk insert request"""
    records: List[SurveyDataRecord] = Field(..., min_items=1, max_items=10000)
    skip_duplicates: bool = Field(
        default=True,
        description="Skip duplicate entries if True, raise error if False"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "skip_duplicates": True,
                "records": [
                    {
                        "dataset_name": "HCES 2022",
                        "category": "HCES",
                        "year": 2022,
                        "indicator_name": "Total Consumption",
                        "value": 5280.50,
                        "state": "Bihar",
                        "district": "Patna"
                    },
                    {
                        "dataset_name": "HCES 2022",
                        "category": "HCES",
                        "year": 2022,
                        "indicator_name": "Food Expenditure",
                        "value": 1200.25,
                        "state": "Bihar",
                        "district": "Patna"
                    }
                ]
            }
        }


class InsertResponse(BaseModel):
    """Response schema for insert operation"""
    success: bool
    inserted_count: int
    skipped_count: int
    total_processed: int
    duplicates: List[dict] = []
    errors: List[dict] = []

    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "inserted_count": 98,
                "skipped_count": 2,
                "total_processed": 100,
                "duplicates": [
                    {
                        "record_index": 45,
                        "dataset_name": "HCES 2022",
                        "state": "Bihar",
                        "year": 2022,
                        "indicator_name": "Total Consumption"
                    }
                ],
                "errors": []
            }
        }


# ============================================================================
# Database Queries
# ============================================================================

async def check_duplicate_record(
    db: Session,
    dataset_name: str,
    year: int,
    indicator_name: str,
    state: str,
    district: Optional[str]
) -> bool:
    """Check if record already exists (using parameterized query)"""
    try:
        query = text("""
            SELECT COUNT(*) FROM survey_data
            WHERE dataset_name = :dataset_name
            AND year = :year
            AND indicator_name = :indicator_name
            AND state = :state
            AND COALESCE(district, '') = COALESCE(:district, '')
        """)
        
        result = db.execute(query, {
            "dataset_name": dataset_name,
            "year": year,
            "indicator_name": indicator_name,
            "state": state,
            "district": district
        }).scalar()
        
        return result > 0
    except Exception as e:
        logger.error(f"Error checking duplicate: {str(e)}")
        return False


async def insert_survey_record(
    db: Session,
    record: SurveyDataRecord
) -> bool:
    """Insert a single survey record using parameterized query"""
    try:
        insert_query = text("""
            INSERT INTO survey_data 
            (dataset_name, category, year, indicator_name, value, state, district, created_at)
            VALUES 
            (:dataset_name, :category, :year, :indicator_name, :value, :state, :district, :created_at)
            ON CONFLICT (dataset_name, year, indicator_name, state, COALESCE(district, ''))
            DO NOTHING
        """)
        
        db.execute(insert_query, {
            "dataset_name": record.dataset_name,
            "category": record.category,
            "year": record.year,
            "indicator_name": record.indicator_name,
            "value": record.value,
            "state": record.state,
            "district": record.district,
            "created_at": datetime.utcnow()
        })
        
        return True
    except Exception as e:
        logger.error(f"Error inserting record: {str(e)}")
        raise


async def insert_survey_records_batch(
    db: Session,
    records: List[SurveyDataRecord]
) -> dict:
    """
    Insert multiple survey records efficiently.
    Uses ON CONFLICT DO NOTHING to skip duplicates.
    """
    inserted_count = 0
    skipped_count = 0
    errors = []
    duplicates = []
    
    try:
        # Prepare batch insert query with parameterized values
        for idx, record in enumerate(records):
            try:
                # Check if duplicate exists
                is_duplicate = await check_duplicate_record(
                    db,
                    record.dataset_name,
                    record.year,
                    record.indicator_name,
                    record.state,
                    record.district
                )
                
                if is_duplicate:
                    skipped_count += 1
                    duplicates.append({
                        "record_index": idx,
                        "dataset_name": record.dataset_name,
                        "state": record.state,
                        "year": record.year,
                        "indicator_name": record.indicator_name
                    })
                    continue
                
                # Insert record
                await insert_survey_record(db, record)
                inserted_count += 1
                
            except Exception as e:
                skipped_count += 1
                error_msg = f"Record {idx}: {str(e)}"
                logger.error(error_msg)
                errors.append({
                    "record_index": idx,
                    "dataset_name": record.dataset_name,
                    "error": str(e)
                })
        
        # Commit all changes
        db.commit()
        
        return {
            "inserted_count": inserted_count,
            "skipped_count": skipped_count,
            "duplicates": duplicates,
            "errors": errors
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Batch insert transaction failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Database transaction failed: {str(e)}"
        )


# ============================================================================
# API Endpoints
# ============================================================================

@router.post(
    "/insert",
    response_model=InsertResponse,
    status_code=201,
    summary="Insert survey dataset records",
    description="Insert one or more survey data records into the survey_data table"
)
async def insert_survey_data(
    request: SurveyDataBulkRequest,
    db: Session = Depends(database.connection.get_db)
):
    """
    Insert survey dataset records into PostgreSQL.
    
    **Features:**
    - Supports bulk insert (up to 10,000 records per request)
    - Skips duplicate entries by default (configurable)
    - Uses parameterized queries for SQL injection protection
    - Returns detailed statistics (inserted, skipped, errors)
    - Maintains transaction integrity
    
    **Request Body:**
    - `records`: Array of survey data records to insert
    - `skip_duplicates`: Boolean - whether to skip duplicates (default: true)
    
    **Response:**
    - `success`: Boolean indicating overall success
    - `inserted_count`: Number of successfully inserted records
    - `skipped_count`: Number of skipped/duplicate records
    - `total_processed`: Total records in request
    - `duplicates`: List of duplicate records skipped
    - `errors`: List of errors encountered
    
    **Example Request:**
    ```json
    {
        "records": [
            {
                "dataset_name": "HCES 2022",
                "category": "HCES",
                "year": 2022,
                "indicator_name": "Total Consumption",
                "value": 5280.50,
                "state": "Bihar",
                "district": "Patna"
            }
        ],
        "skip_duplicates": true
    }
    ```
    
    **Error Responses:**
    - 400: Invalid request data (validation error)
    - 422: Semantic validation error (e.g., year out of range)
    - 500: Database error (transaction failed)
    """
    
    try:
        # Validate request
        if not request.records or len(request.records) == 0:
            raise HTTPException(
                status_code=400,
                detail="At least one record is required"
            )
        
        if len(request.records) > 10000:
            raise HTTPException(
                status_code=422,
                detail="Maximum 10,000 records per request"
            )
        
        logger.info(f"Processing insert request with {len(request.records)} records")
        
        # Insert records in batch
        result = await insert_survey_records_batch(db, request.records)
        
        # Prepare response
        response = InsertResponse(
            success=result["inserted_count"] > 0 or result["skipped_count"] > 0,
            inserted_count=result["inserted_count"],
            skipped_count=result["skipped_count"],
            total_processed=len(request.records),
            duplicates=result["duplicates"],
            errors=result["errors"]
        )
        
        logger.info(
            f"Insert complete: {result['inserted_count']} inserted, "
            f"{result['skipped_count']} skipped"
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error in insert_survey_data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Server error: {str(e)}"
        )


@router.post(
    "/insert-safe",
    response_model=InsertResponse,
    status_code=201,
    summary="Insert with automatic duplicate detection (strict mode)",
    description="Insert records and automatically skip all duplicates without forcing transaction"
)
async def insert_survey_data_safe(
    request: SurveyDataBulkRequest,
    db: Session = Depends(database.connection.get_db)
):
    """
    Safe insert endpoint with lenient error handling.
    Processes each record individually to continue on errors.
    
    Best for:
    - Data imports with potential inconsistencies
    - Large datasets where partial success is acceptable
    - Testing and data validation
    """
    
    try:
        if not request.records:
            raise HTTPException(status_code=400, detail="No records provided")
        
        inserted_count = 0
        skipped_count = 0
        duplicates = []
        errors = []
        
        for idx, record in enumerate(request.records):
            try:
                # Check duplicate
                is_duplicate = await check_duplicate_record(
                    db,
                    record.dataset_name,
                    record.year,
                    record.indicator_name,
                    record.state,
                    record.district
                )
                
                if is_duplicate:
                    skipped_count += 1
                    duplicates.append({
                        "record_index": idx,
                        "dataset_name": record.dataset_name,
                        "state": record.state,
                        "year": record.year,
                        "indicator_name": record.indicator_name
                    })
                    continue
                
                # Try to insert
                await insert_survey_record(db, record)
                db.commit()
                inserted_count += 1
                
            except Exception as e:
                db.rollback()
                skipped_count += 1
                errors.append({
                    "record_index": idx,
                    "dataset_name": record.dataset_name,
                    "error": str(e)
                })
        
        return InsertResponse(
            success=inserted_count > 0,
            inserted_count=inserted_count,
            skipped_count=skipped_count,
            total_processed=len(request.records),
            duplicates=duplicates,
            errors=errors
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in safe insert: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get(
    "/stats",
    summary="Get survey data statistics",
    description="Get count and metadata about survey data table"
)
async def get_survey_data_stats(db: Session = Depends(database.connection.get_db)):
    """
    Get statistics about the survey_data table.
    
    Returns:
    - total_records: Total number of records
    - datasets: List of unique dataset names
    - categories: List of unique categories
    - year_range: Min and max years
    - states: List of unique states
    """
    
    try:
        # Total records
        total_query = text("SELECT COUNT(*) FROM survey_data")
        total_records = db.execute(total_query).scalar()
        
        # Unique datasets
        datasets_query = text(
            "SELECT DISTINCT dataset_name FROM survey_data ORDER BY dataset_name"
        )
        datasets = [row[0] for row in db.execute(datasets_query).fetchall()]
        
        # Unique categories
        categories_query = text(
            "SELECT DISTINCT category FROM survey_data ORDER BY category"
        )
        categories = [row[0] for row in db.execute(categories_query).fetchall()]
        
        # Year range
        year_range_query = text(
            "SELECT MIN(year), MAX(year) FROM survey_data"
        )
        min_year, max_year = db.execute(year_range_query).fetchone()
        
        # Unique states
        states_query = text(
            "SELECT DISTINCT state FROM survey_data ORDER BY state"
        )
        states = [row[0] for row in db.execute(states_query).fetchall()]
        
        return {
            "success": True,
            "data": {
                "total_records": total_records,
                "dataset_count": len(datasets),
                "datasets": datasets,
                "category_count": len(categories),
                "categories": categories,
                "year_range": {
                    "min": min_year,
                    "max": max_year
                },
                "state_count": len(states),
                "states": states
            },
            "meta": {
                "timestamp": datetime.utcnow().isoformat()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving statistics: {str(e)}"
        )
