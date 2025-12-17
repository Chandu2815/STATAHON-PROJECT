"""
Query API endpoints
"""
from fastapi import APIRouter, Depends, Query as QueryParam, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, Dict, Any
from app.database import get_db
from app.models.user import User
from app.schemas.dataset import QueryResponse
from app.auth import get_current_user
from app.services.query_builder import QueryBuilderService
from app.services.access_control import AccessControlService
from app.services.payment import PaymentService
import json

router = APIRouter(prefix="/query", tags=["Query"])


@router.get("", response_model=QueryResponse)
def query_data(
    dataset: str = QueryParam(..., description="Dataset name to query"),
    state: Optional[str] = QueryParam(None, description="Filter by state"),
    district: Optional[str] = QueryParam(None, description="Filter by district"),
    gender: Optional[str] = QueryParam(None, description="Filter by gender"),
    age: Optional[str] = QueryParam(None, description="Filter by age group", alias="age_group"),
    year: Optional[int] = QueryParam(None, description="Filter by year"),
    limit: int = QueryParam(100, ge=1, le=10000, description="Maximum records to return"),
    offset: int = QueryParam(0, ge=0, description="Number of records to skip"),
    order_by: Optional[str] = QueryParam(None, description="Field to order by"),
    order_direction: str = QueryParam("asc", description="Order direction (asc/desc)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Query data with multi-dimensional filters
    
    Example: /query?dataset=census&state=Maharashtra&gender=female&age_group=15-29
    """
    
    # Check rate limits and access control
    access_control = AccessControlService(db)
    access_control.check_rate_limit(current_user)
    
    # Build filters
    filters = {}
    if state:
        filters['state'] = state
    if district:
        filters['district'] = district
    if gender:
        filters['gender'] = gender
    if age:
        filters['age_group'] = age
    if year:
        filters['year'] = year
    
    # Execute query
    query_builder = QueryBuilderService(db)
    
    if dataset.lower() == "census":
        result = query_builder.execute_census_query(
            filters=filters,
            limit=limit,
            offset=offset,
            order_by=order_by,
            order_direction=order_direction
        )
    else:
        result = query_builder.execute_generic_query(
            dataset_name=dataset,
            filters=filters,
            limit=limit,
            offset=offset
        )
    
    # Calculate response size
    response_size = len(json.dumps(result))
    
    # Check volume limits
    access_control.check_volume_limit(current_user, response_size)
    
    # Charge for query (if applicable)
    payment_service = PaymentService(db)
    payment_service.charge_for_query(current_user, response_size)
    
    # Log usage
    access_control.log_usage(
        user=current_user,
        endpoint="/api/v1/query",
        method="GET",
        dataset_name=dataset,
        query_params=json.dumps(filters),
        response_size=response_size
    )
    
    return result


@router.post("", response_model=QueryResponse)
def advanced_query(
    query_params: Dict[str, Any],
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Advanced query endpoint with complex filters and aggregations
    
    Example body:
    {
        "dataset": "census",
        "filters": {
            "state": "Maharashtra",
            "gender": "female",
            "age_group": "15-29"
        },
        "fields": ["state", "gender", "population"],
        "limit": 100,
        "offset": 0
    }
    """
    
    # Check rate limits
    access_control = AccessControlService(db)
    access_control.check_rate_limit(current_user)
    
    # Extract parameters
    dataset = query_params.get('dataset')
    filters = query_params.get('filters', {})
    fields = query_params.get('fields')
    limit = query_params.get('limit', 100)
    offset = query_params.get('offset', 0)
    order_by = query_params.get('order_by')
    order_direction = query_params.get('order_direction', 'asc')
    
    if not dataset:
        raise HTTPException(status_code=400, detail="Dataset name is required")
    
    # Execute query
    query_builder = QueryBuilderService(db)
    
    if dataset.lower() == "census":
        result = query_builder.execute_census_query(
            filters=filters,
            fields=fields,
            limit=limit,
            offset=offset,
            order_by=order_by,
            order_direction=order_direction
        )
    else:
        result = query_builder.execute_generic_query(
            dataset_name=dataset,
            filters=filters,
            fields=fields,
            limit=limit,
            offset=offset
        )
    
    # Calculate response size and log usage
    response_size = len(json.dumps(result))
    
    # Check volume limits
    access_control.check_volume_limit(current_user, response_size)
    
    # Charge for query
    payment_service = PaymentService(db)
    payment_service.charge_for_query(current_user, response_size)
    
    # Log usage
    access_control.log_usage(
        user=current_user,
        endpoint="/api/v1/query",
        method="POST",
        dataset_name=dataset,
        query_params=json.dumps(filters),
        response_size=response_size
    )
    
    return result
