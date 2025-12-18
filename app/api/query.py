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
    dataset: int = QueryParam(..., description="Dataset ID to query"),
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
    Query data with multi-dimensional filters using dataset ID
    
    Example: /query?dataset=2&state=TELANGANA
    Example: /query?dataset=4&limit=100
    
    Available dataset IDs:
    - 1: Data Layout
    - 2: District Codes  
    - 3: Item Codes
    - 4: Household Survey
    - 5: Person Survey
    """
    from app.models.dataset import Dataset
    
    # Check rate limits and access control
    access_control = AccessControlService(db)
    access_control.check_rate_limit(current_user)
    
    # Get dataset by ID
    dataset_obj = db.query(Dataset).filter(Dataset.id == dataset).first()
    if not dataset_obj:
        raise HTTPException(status_code=404, detail=f"Dataset with ID {dataset} not found")
    
    # Check if dataset uses dedicated table or data_records
    from sqlalchemy import inspect
    inspector = inspect(db.bind)
    has_dedicated_table = dataset_obj.table_name in inspector.get_table_names()
    
    # Map of state names to codes (for convenience)
    STATE_CODES = {
        'TELANGANA': 36, 'ANDHRA PRADESH': 28, 'KARNATAKA': 29,
        'TAMIL NADU': 33, 'KERALA': 32, 'MAHARASHTRA': 27,
        'PUNJAB': 3, 'HARYANA': 6, 'DELHI': 7, 'UTTAR PRADESH': 9,
        'BIHAR': 10, 'WEST BENGAL': 19, 'GUJARAT': 24, 'RAJASTHAN': 8
    }
    
    # Build filters - map generic names to actual column names
    filters = {}
    
    if has_dedicated_table:
        # For dedicated tables (household_survey, person_survey), map to actual columns
        if state:
            # Try to convert state name to code
            if state.isdigit():
                filters['State_UT_Code'] = int(state)
            elif state.upper() in STATE_CODES:
                filters['State_UT_Code'] = STATE_CODES[state.upper()]
        
        if district:
            # District should be a code
            if district.isdigit():
                filters['District_Code'] = int(district)
            elif district.upper() == 'NIRMAL':
                filters['District_Code'] = 4  # Nirmal district code
        
        if gender:
            # For person survey: Sex column (1=Male, 2=Female, 3=Transgender)
            gender_upper = gender.upper()
            if gender_upper in ['MALE', 'M', '1']:
                filters['Sex'] = 1
            elif gender_upper in ['FEMALE', 'F', '2']:
                filters['Sex'] = 2
            elif gender_upper in ['TRANSGENDER', 'T', '3']:
                filters['Sex'] = 3
        
        if age:
            # Parse age range like "15-29"
            if '-' in age:
                age_parts = age.split('-')
                if len(age_parts) == 2:
                    filters['Age'] = {
                        '$gte': int(age_parts[0]),
                        '$lte': int(age_parts[1])
                    }
            elif age.isdigit():
                filters['Age'] = int(age)
    else:
        # For JSON-based storage (data_records)
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
    
    if dataset_obj.name.lower().startswith("census"):
        result = query_builder.execute_census_query(
            filters=filters,
            limit=limit,
            offset=offset,
            order_by=order_by,
            order_direction=order_direction
        )
    elif has_dedicated_table:
        # Use table query for dedicated tables
        result = query_builder.execute_table_query(
            table_name=dataset_obj.table_name,
            filters=filters,
            fields=None,
            limit=limit,
            offset=offset
        )
    else:
        # Use generic query for data_records JSON storage
        result = query_builder.execute_generic_query(
            dataset_name=dataset_obj.name,
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
        dataset_name=dataset_obj.name,
        query_params=json.dumps(filters),
        response_size=response_size
    )
    
    return result


@router.get("/{table_name}", response_model=QueryResponse)
def query_table(
    table_name: str,
    filters: Optional[str] = QueryParam(None, description="JSON filters (e.g., {'State_Ut_Code': 28})"),
    limit: int = QueryParam(100, ge=1, le=10000, description="Maximum records to return"),
    offset: int = QueryParam(0, ge=0, description="Number of records to skip"),
    fields: Optional[str] = QueryParam(None, description="Comma-separated fields to return"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Query any survey table directly by table name with JSON filters
    
    **Available PLFS Survey Tables:**
    - `household_survey`: PLFS Household data (CHHV1) with 41 columns
    - `person_survey`: PLFS Person-level data (CPERV1) with 140+ columns
    
    **Filter Operators:**
    - Equality: `{"State_Ut_Code": 28}`
    - Greater than/equal: `{"Age": {"$gte": 25}}`
    - Less than/equal: `{"Age": {"$lte": 35}}`
    - Range: `{"Age": {"$gte": 25, "$lte": 35}}`
    - In list: `{"State_Ut_Code": {"$in": [28, 29, 30]}}`
    - Not equal: `{"Sex": {"$ne": 1}}`
    
    **Examples:**
    
    Get households in Maharashtra (State_Ut_Code=28):
    ```
    GET /api/v1/query/household_survey?filters={"State_Ut_Code": 28}&limit=10
    ```
    
    Get persons aged 25-35 who are employed:
    ```
    GET /api/v1/query/person_survey?filters={"Age": {"$gte": 25, "$lte": 35}, "Current_Weekly_Activity_Status": 11}
    ```
    
    Get specific fields only:
    ```
    GET /api/v1/query/household_survey?fields=State_Ut_Code,District_Code,Monthly_Consumer_Expenditure&limit=50
    ```
    
    **Field Selection:**
    - Omit `fields` to get all columns
    - Use `fields=col1,col2,col3` to get specific columns only
    
    **Note:** To see available tables, use `GET /api/v1/datasets/tables`
    """
    
    # Check rate limits
    access_control = AccessControlService(db)
    access_control.check_rate_limit(current_user)
    
    # Parse filters
    filter_dict = {}
    if filters:
        try:
            filter_dict = json.loads(filters)
        except json.JSONDecodeError:
            raise HTTPException(
                status_code=400,
                detail="Invalid JSON in filters parameter"
            )
    
    # Parse fields
    field_list = None
    if fields:
        field_list = [f.strip() for f in fields.split(',')]
    
    # Execute query using raw SQL for dynamic table access
    from sqlalchemy import text, inspect
    
    # Verify table exists
    inspector = inspect(db.bind)
    if table_name not in inspector.get_table_names():
        raise HTTPException(
            status_code=404,
            detail=f"Table '{table_name}' not found"
        )
    
    # Build query
    query_builder = QueryBuilderService(db)
    result = query_builder.execute_table_query(
        table_name=table_name,
        filters=filter_dict,
        fields=field_list,
        limit=limit,
        offset=offset
    )
    
    # Calculate response size
    response_size = len(json.dumps(result))
    
    # Check volume limits
    access_control.check_volume_limit(current_user, response_size)
    
    # Charge for query
    payment_service = PaymentService(db)
    payment_service.charge_for_query(current_user, response_size)
    
    # Log usage
    access_control.log_usage(
        user=current_user,
        endpoint=f"/api/v1/query/{table_name}",
        method="GET",
        dataset_name=table_name,
        query_params=json.dumps(filter_dict),
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


@router.get("/dataset/{dataset_id}/records")
def query_dataset_by_id(
    dataset_id: int,
    filters: Optional[str] = QueryParam(None, description="JSON filters"),
    limit: int = QueryParam(100, ge=1, le=10000),
    offset: int = QueryParam(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Query dataset by ID - handles both dedicated tables and data_records storage
    
    Works for all dataset types:
    - Datasets with dedicated tables (household_survey, person_survey)
    - Datasets using data_records JSON storage (district codes, item codes, etc.)
    """
    from app.models.dataset import Dataset, DataRecord
    from sqlalchemy import inspect
    
    # Check rate limits
    access_control = AccessControlService(db)
    access_control.check_rate_limit(current_user)
    
    # Get dataset
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Parse filters
    filter_dict = {}
    if filters:
        try:
            filter_dict = json.loads(filters)
        except json.JSONDecodeError:
            raise HTTPException(status_code=400, detail="Invalid JSON in filters")
    
    # Check if dataset uses dedicated table or data_records
    inspector = inspect(db.bind)
    
    if dataset.table_name in inspector.get_table_names():
        # Use dedicated table
        query_builder = QueryBuilderService(db)
        result = query_builder.execute_table_query(
            table_name=dataset.table_name,
            filters=filter_dict,
            fields=None,
            limit=limit,
            offset=offset
        )
    else:
        # Use data_records table
        query = db.query(DataRecord).filter(DataRecord.dataset_id == dataset_id)
        
        # Apply filters to JSON data
        all_records = query.all()
        filtered_records = []
        
        for record in all_records:
            match = True
            for key, value in filter_dict.items():
                if key not in record.data or record.data[key] != value:
                    match = False
                    break
            if match:
                filtered_records.append(record.data)
        
        # Apply pagination
        total = len(filtered_records)
        paginated = filtered_records[offset:offset + limit]
        
        result = {
            'data': paginated,
            'total': total,
            'limit': limit,
            'offset': offset,
            'dataset_id': dataset_id,
            'dataset_name': dataset.name,
            'storage_type': 'data_records (JSON)'
        }
    
    # Calculate response size
    response_size = len(json.dumps(result))
    
    # Check volume limits
    access_control.check_volume_limit(current_user, response_size)
    
    # Charge for query
    payment_service = PaymentService(db)
    payment_service.charge_for_query(current_user, response_size)
    
    # Log usage
    access_control.log_usage(
        user=current_user,
        endpoint=f"/api/v1/query/dataset/{dataset_id}/records",
        method="GET",
        dataset_name=dataset.name,
        query_params=json.dumps(filter_dict),
        response_size=response_size
    )
    
    return result
