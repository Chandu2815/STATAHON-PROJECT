"""
Dataset management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import inspect, text
from typing import List
from app.database import get_db
from app.models import Dataset
from app.models.user import User, UserRole
from app.schemas.dataset import DatasetCreate, DatasetUpdate, DatasetResponse
from app.auth import get_current_user
from app.services.access_control import AccessControlService

router = APIRouter(prefix="/datasets", tags=["Datasets"])


@router.get("/tables")
def list_available_tables(db: Session = Depends(get_db)):
    """
    List all available survey tables in the database (PUBLIC)
    
    This endpoint shows all PLFS survey tables that can be queried,
    including household_survey and person_survey.
    
    **No authentication required** - Public endpoint for dataset discovery.
    
    Returns:
    - table_name: Name of the database table
    - row_count: Number of records
    - columns: List of column names
    - registered: Whether it's registered in datasets table
    - dataset_id: ID if registered (for use with other endpoints)
    """
    inspector = inspect(db.bind)
    all_tables = inspector.get_table_names()
    
    # Filter for survey tables and relevant data tables
    survey_tables = [t for t in all_tables if any(keyword in t.lower() for keyword in 
                     ['survey', 'plfs', 'census', 'data_plfs'])]
    
    results = []
    registered_datasets = {d.table_name: d for d in db.query(Dataset).all()}
    
    for table in survey_tables:
        try:
            # Get row count
            count_result = db.execute(text(f"SELECT COUNT(*) FROM {table}"))
            row_count = count_result.scalar()
            
            # Get columns
            columns = inspector.get_columns(table)
            column_names = [col['name'] for col in columns]
            
            # Check if registered
            is_registered = table in registered_datasets
            dataset_id = registered_datasets[table].id if is_registered else None
            dataset_name = registered_datasets[table].name if is_registered else None
            
            results.append({
                'table_name': table,
                'display_name': dataset_name or table.replace('_', ' ').title(),
                'row_count': row_count,
                'column_count': len(column_names),
                'sample_columns': column_names[:5] if len(column_names) > 5 else column_names,
                'registered': is_registered,
                'dataset_id': dataset_id,
                'query_endpoint': f"/api/v1/query/{table}",
                'schema_endpoint': f"/api/v1/datasets/{dataset_id}/schema" if dataset_id else None
            })
        except Exception as e:
            print(f"Error processing table {table}: {e}")
            continue
    
    return {
        'total_tables': len(results),
        'tables': results,
        'note': 'Use /api/v1/query/{table_name} to query any table'
    }


@router.get("", response_model=List[DatasetResponse])
def list_datasets(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all available datasets"""
    datasets = db.query(Dataset).offset(skip).limit(limit).all()
    return datasets


@router.get("/{dataset_id}", response_model=DatasetResponse)
def get_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dataset details by ID"""
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    return dataset


@router.post("", response_model=DatasetResponse, status_code=status.HTTP_201_CREATED)
def create_dataset(
    dataset_data: DatasetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new dataset (Admin only)"""
    
    # Check admin permission
    access_control = AccessControlService(db)
    access_control.check_permission(current_user, UserRole.ADMIN)
    
    # Check if dataset already exists
    existing_dataset = db.query(Dataset).filter(
        (Dataset.name == dataset_data.name) | (Dataset.table_name == dataset_data.table_name)
    ).first()
    
    if existing_dataset:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dataset with this name or table name already exists"
        )
    
    # Create dataset
    dataset = Dataset(**dataset_data.dict())
    db.add(dataset)
    db.commit()
    db.refresh(dataset)
    
    return dataset


@router.put("/{dataset_id}", response_model=DatasetResponse)
def update_dataset(
    dataset_id: int,
    dataset_data: DatasetUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update dataset metadata (Admin only)"""
    
    # Check admin permission
    access_control = AccessControlService(db)
    access_control.check_permission(current_user, UserRole.ADMIN)
    
    # Find dataset
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    # Update fields
    update_data = dataset_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(dataset, field, value)
    
    db.commit()
    db.refresh(dataset)
    
    return dataset


@router.delete("/{dataset_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_dataset(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a dataset (Admin only)"""
    
    # Check admin permission
    access_control = AccessControlService(db)
    access_control.check_permission(current_user, UserRole.ADMIN)
    
    # Find dataset
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    db.delete(dataset)
    db.commit()
    
    return None


@router.get("/{dataset_id}/schema")
def get_dataset_schema(
    dataset_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get dataset schema information including columns and types"""
    from sqlalchemy import inspect
    from app.models.dataset import DataRecord
    
    # Get dataset
    dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not dataset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dataset not found"
        )
    
    # Get table schema from database
    inspector = inspect(db.bind)
    
    # Check if this dataset uses a dedicated table or data_records
    if dataset.table_name not in inspector.get_table_names():
        # Check if data exists in data_records table
        record_count = db.query(DataRecord).filter(DataRecord.dataset_id == dataset.id).count()
        
        if record_count > 0:
            # Dataset uses data_records table (old JSON-based storage)
            # Get schema from config or sample record
            sample_record = db.query(DataRecord).filter(DataRecord.dataset_id == dataset.id).first()
            
            schema_info = []
            if sample_record and sample_record.data:
                for key in sample_record.data.keys():
                    schema_info.append({
                        'name': key,
                        'type': 'JSON (dynamic)',
                        'nullable': True,
                        'default': None
                    })
            
            return {
                'dataset_id': dataset.id,
                'dataset_name': dataset.name,
                'table_name': 'data_records',
                'description': dataset.description,
                'storage_type': 'JSON-based (data_records table)',
                'columns': schema_info,
                'config_schema': dataset.config.get('schema', []) if dataset.config else [],
                'row_count': record_count,
                'note': 'This dataset uses JSON storage in data_records table'
            }
        else:
            return {
                'dataset_id': dataset.id,
                'dataset_name': dataset.name,
                'table_name': dataset.table_name,
                'config_schema': dataset.config.get('schema', []) if dataset.config else [],
                'note': 'Table not yet created and no data in data_records'
            }
    
    # Dataset has a dedicated table
    # Get columns
    columns = inspector.get_columns(dataset.table_name)
    
    schema_info = []
    for col in columns:
        schema_info.append({
            'name': col['name'],
            'type': str(col['type']),
            'nullable': col['nullable'],
            'default': str(col['default']) if col['default'] else None
        })
    
    # Get indexes
    indexes = inspector.get_indexes(dataset.table_name)
    
    # Get row count
    row_count = db.execute(text(f"SELECT COUNT(*) FROM {dataset.table_name}")).scalar()
    
    return {
        'dataset_id': dataset.id,
        'dataset_name': dataset.name,
        'table_name': dataset.table_name,
        'description': dataset.description,
        'storage_type': 'Dedicated table',
        'columns': schema_info,
        'indexes': indexes,
        'config_schema': dataset.config.get('schema', []) if dataset.config else [],
        'row_count': row_count
    }
