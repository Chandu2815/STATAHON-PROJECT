"""
Dataset management API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Dataset
from app.models.user import User, UserRole
from app.schemas.dataset import DatasetCreate, DatasetUpdate, DatasetResponse
from app.auth import get_current_user
from app.services.access_control import AccessControlService

router = APIRouter(prefix="/datasets", tags=["Datasets"])


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
