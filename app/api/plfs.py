"""
API endpoints for PLFS (Periodic Labour Force Survey) data
"""
from fastapi import APIRouter, Depends, Query as QueryParam, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any
from app.database import get_db
from app.models import Dataset, DataRecord
from app.models.user import User
from app.auth import get_current_user
from app.services.access_control import AccessControlService
import json

router = APIRouter(prefix="/plfs", tags=["PLFS Data"])


@router.get("/datasets", response_model=List[Dict[str, Any]])
def list_plfs_datasets(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    List all available PLFS datasets
    """
    datasets = db.query(Dataset).filter(
        Dataset.name.like('PLFS%')
    ).all()
    
    result = []
    for ds in datasets:
        record_count = db.query(DataRecord).filter(
            DataRecord.dataset_id == ds.id
        ).count()
        
        result.append({
            'id': ds.id,
            'name': ds.name,
            'description': ds.description,
            'record_count': record_count,
            'created_at': ds.created_at.isoformat() if ds.created_at else None
        })
    
    return result


@router.get("/dataset/{dataset_id}/records")
def get_plfs_records(
    dataset_id: int,
    limit: int = QueryParam(100, ge=1, le=1000),
    offset: int = QueryParam(0, ge=0),
    sheet: Optional[str] = QueryParam(None, description="Filter by sheet name"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get records from a PLFS dataset
    """
    # Check rate limits
    access_control = AccessControlService(db)
    access_control.check_rate_limit(current_user)
    
    # Get dataset
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(status_code=404, detail="Dataset not found")
    
    # Build query
    query = db.query(DataRecord).filter(DataRecord.dataset_id == dataset_id)
    
    # Filter by sheet if provided
    if sheet:
        # This requires checking JSON field - SQLite doesn't support JSON queries well
        # For PostgreSQL, you would use: query = query.filter(DataRecord.data['sheet'].astext == sheet)
        pass
    
    total_count = query.count()
    records = query.limit(limit).offset(offset).all()
    
    # Extract data
    data = [record.data for record in records]
    
    # Log usage
    response_size = len(json.dumps(data))
    access_control.check_volume_limit(current_user, response_size)
    access_control.log_usage(
        user=current_user,
        endpoint="/api/v1/plfs/dataset/{dataset_id}/records",
        method="GET",
        dataset_name=dataset.name,
        query_params=f"limit={limit}&offset={offset}&sheet={sheet}",
        response_size=response_size
    )
    
    return {
        'dataset_id': dataset_id,
        'dataset_name': dataset.name,
        'total_records': total_count,
        'returned_records': len(data),
        'limit': limit,
        'offset': offset,
        'data': data
    }


@router.get("/district-codes")
def get_district_codes(
    state: Optional[str] = QueryParam(None, description="Filter by state name"),
    limit: int = QueryParam(100, ge=1, le=1000),
    offset: int = QueryParam(0, ge=0),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get district codes from PLFS data
    """
    # Find district codes dataset
    dataset = db.query(Dataset).filter(
        Dataset.name.like('%District_codes%')
    ).first()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="District codes dataset not found")
    
    # Get records
    query = db.query(DataRecord).filter(DataRecord.dataset_id == dataset.id)
    
    total_count = query.count()
    
    # Helper function to rename fields for better readability
    def rename_district_fields(record):
        """Rename Unnamed columns to meaningful names"""
        renamed = record.copy()
        if 'Unnamed: 1' in renamed:
            renamed['STATE_NAME'] = renamed.pop('Unnamed: 1')
        if 'Unnamed: 2' in renamed:
            renamed['DISTRICT_CODE'] = renamed.pop('Unnamed: 2')
        if 'Unnamed: 3' in renamed:
            renamed['DISTRICT_NAME'] = renamed.pop('Unnamed: 3')
        return renamed
    
    # If filtering by state, fetch ALL records first, then filter
    # (because SQLite doesn't support JSON querying efficiently)
    if state:
        # Fetch all records
        all_records = query.all()
        all_data = [record.data for record in all_records]
        
        # Filter by state - the state name is stored in 'Unnamed: 1' field from Excel import
        filtered_data = [d for d in all_data if state.lower() in str(d.get('Unnamed: 1', '')).lower()]
        
        # Apply pagination to filtered results
        paginated_data = filtered_data[offset:offset + limit]
        
        # Rename fields for better readability
        data = [rename_district_fields(d) for d in paginated_data]
        
        return {
            'total_records': total_count,
            'filtered_count': len(filtered_data),
            'returned_records': len(data),
            'data': data
        }
    else:
        # No filter - just apply pagination directly
        records = query.limit(limit).offset(offset).all()
        raw_data = [record.data for record in records]
        
        # Rename fields for better readability
        data = [rename_district_fields(d) for d in raw_data]
        
        return {
            'total_records': total_count,
            'returned_records': len(data),
            'data': data
        }


@router.get("/data-layout")
def get_plfs_data_layout(
    block: Optional[str] = QueryParam(None, description="Filter by block name"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get PLFS data layout information
    """
    # Find data layout dataset
    dataset = db.query(Dataset).filter(
        Dataset.name.like('%Data_Layout%')
    ).first()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Data layout dataset not found")
    
    # Get all records
    records = db.query(DataRecord).filter(
        DataRecord.dataset_id == dataset.id
    ).all()
    
    data = [record.data for record in records]
    
    # Filter by block if provided
    if block:
        data = [d for d in data if block.lower() in str(d.get('Block', '')).lower()]
    
    return {
        'total_records': len(data),
        'data': data
    }


@router.get("/item-codes")
def get_plfs_item_codes(
    block: Optional[str] = QueryParam(None, description="Filter by block (e.g., 'Block 1', 'Block 4')"),
    search: Optional[str] = QueryParam(None, description="Search in item descriptions"),
    limit: int = QueryParam(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get PLFS item codes and descriptions
    """
    # Find item codes dataset
    dataset = db.query(Dataset).filter(
        Dataset.name.like('%Item Code Description%')
    ).first()
    
    if not dataset:
        raise HTTPException(status_code=404, detail="Item codes dataset not found")
    
    # Get records
    records = db.query(DataRecord).filter(
        DataRecord.dataset_id == dataset.id
    ).limit(limit).all()
    
    data = [record.data for record in records]
    
    # Filter by sheet/block if provided
    if block:
        data = [d for d in data if block.lower() in str(d.get('sheet', '')).lower()]
    
    # Search in descriptions
    if search:
        search_lower = search.lower()
        data = [
            d for d in data 
            if search_lower in str(d.get('Item Description', '')).lower() or
               search_lower in str(d.get('Item Code', '')).lower()
        ]
    
    return {
        'total_records': len(data),
        'data': data
    }


@router.get("/summary")
def get_plfs_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get summary of all PLFS data available
    """
    datasets = db.query(Dataset).filter(
        Dataset.name.like('PLFS%')
    ).all()
    
    summary = {
        'total_datasets': len(datasets),
        'datasets': []
    }
    
    for ds in datasets:
        record_count = db.query(DataRecord).filter(
            DataRecord.dataset_id == ds.id
        ).count()
        
        # Get sample record to show structure
        sample = db.query(DataRecord).filter(
            DataRecord.dataset_id == ds.id
        ).first()
        
        sample_keys = list(sample.data.keys()) if sample else []
        
        summary['datasets'].append({
            'id': ds.id,
            'name': ds.name,
            'description': ds.description,
            'record_count': record_count,
            'sample_fields': sample_keys[:10]  # First 10 fields
        })
    
    return summary
