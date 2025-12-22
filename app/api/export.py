"""
Data visualization endpoints for charts and tables
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.user import User
from app.auth import get_current_user
from app.services.export import ExportService
from app.services.access_control import AccessControlService

router = APIRouter(prefix="/export", tags=["Data Export & Visualization"])


@router.get("/csv")
def export_to_csv(
    dataset: str = Query(..., description="Dataset name to export"),
    limit: int = Query(100, description="Maximum records to export"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Export data in CSV format (developer-friendly)
    
    **Expected Outcome Alignment:**
    - Presents results in developer-friendly CSV format
    
    **Example:**
    ```
    GET /api/v1/export/csv?dataset=plfs_districts&limit=100
    ```
    
    Returns CSV file for download
    """
    # Check access control
    access_control = AccessControlService(db)
    access_control.check_rate_limit(current_user)
    
    # Get data based on dataset
    if dataset == "plfs_districts":
        from app.models.user import PLFSData
        records = db.query(PLFSData).filter(
            PLFSData.dataset_name == "District_codes_PLFS"
        ).limit(limit).all()
        
        data = [
            {
                "state": r.data.get("Unnamed: 1"),
                "district": r.data.get("Unnamed: 3"),
                "nss_code": r.data.get("Unnamed: 2")
            }
            for r in records
        ]
    elif dataset == "plfs_items":
        from app.models.user import PLFSData
        records = db.query(PLFSData).filter(
            PLFSData.dataset_name == "PLFS_Item_Codes"
        ).limit(limit).all()
        
        data = [
            {
                "item": r.data.get("Unnamed: 1"),
                "code": r.data.get("Unnamed: 3"),
                "block": r.sheet
            }
            for r in records
        ]
    else:
        data = []
    
    # Log usage
    access_control.log_usage(
        user=current_user,
        endpoint="/export/csv",
        method="GET",
        dataset_name=dataset,
        response_size=len(str(data))
    )
    
    # Export to CSV
    export_service = ExportService()
    return export_service.export_to_csv(data, filename=f"{dataset}_export.csv")


@router.get("/chart")
def get_chart_data(
    dataset: str = Query(..., description="Dataset name"),
    x_field: str = Query(..., description="Field for X-axis"),
    y_field: str = Query(..., description="Field for Y-axis"),
    limit: int = Query(20, description="Maximum data points"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get data formatted for chart visualization (visual format for end users)
    
    **Expected Outcome Alignment:**
    - Presents results in visual formats (charts) for end users
    
    **Example:**
    ```
    GET /api/v1/export/chart?dataset=usage&x_field=date&y_field=requests
    ```
    
    Returns Chart.js compatible data structure
    """
    # Check access control
    access_control = AccessControlService(db)
    access_control.check_rate_limit(current_user)
    
    # Get usage data for charts
    from app.models.user import UsageLog
    from datetime import datetime, timedelta
    from sqlalchemy import func
    
    # Get last N days of usage
    start_date = datetime.utcnow() - timedelta(days=limit)
    
    usage_by_date = db.query(
        func.date(UsageLog.timestamp).label('date'),
        func.count(UsageLog.id).label('requests')
    ).filter(
        UsageLog.user_id == current_user.id,
        UsageLog.timestamp >= start_date
    ).group_by(func.date(UsageLog.timestamp)).all()
    
    data = [
        {"date": str(row.date), "requests": row.requests}
        for row in usage_by_date
    ]
    
    # Prepare chart data
    export_service = ExportService()
    chart_data = export_service.prepare_chart_data(data, x_field, y_field)
    
    return {
        "chart_data": chart_data,
        "raw_data": data,
        "format": "Chart.js compatible",
        "visualization_type": "bar_chart"
    }


@router.get("/table")
def get_table_data(
    dataset: str = Query(..., description="Dataset name"),
    limit: int = Query(50, description="Maximum rows"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get data formatted for table visualization (visual format for end users)
    
    **Expected Outcome Alignment:**
    - Presents results in visual formats (tables) for end users
    
    **Example:**
    ```
    GET /api/v1/export/table?dataset=plfs_districts&limit=50
    ```
    
    Returns structured table data with headers and rows
    """
    # Check access control
    access_control = AccessControlService(db)
    access_control.check_rate_limit(current_user)
    
    # Get data
    if dataset == "plfs_districts":
        from app.models.user import PLFSData
        records = db.query(PLFSData).filter(
            PLFSData.dataset_name == "District_codes_PLFS"
        ).limit(limit).all()
        
        data = [
            {
                "State": r.data.get("Unnamed: 1", ""),
                "District": r.data.get("Unnamed: 3", ""),
                "NSS Code": r.data.get("Unnamed: 2", "")
            }
            for r in records
        ]
    elif dataset == "plfs_items":
        from app.models.user import PLFSData
        records = db.query(PLFSData).filter(
            PLFSData.dataset_name == "PLFS_Item_Codes"
        ).limit(limit).all()
        
        data = [
            {
                "Item": r.data.get("Unnamed: 1", ""),
                "Code": r.data.get("Unnamed: 3", ""),
                "Block": r.sheet or ""
            }
            for r in records
        ]
    else:
        data = []
    
    # Prepare table data
    export_service = ExportService()
    table_data = export_service.prepare_table_data(data, limit)
    
    return {
        "table": table_data,
        "format": "structured_table",
        "visualization_type": "data_table"
    }
