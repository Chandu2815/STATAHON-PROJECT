"""
Pydantic schemas for datasets
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class DatasetBase(BaseModel):
    """Base dataset schema"""
    name: str = Field(..., description="Dataset name")
    description: Optional[str] = Field(None, description="Dataset description")
    table_name: str = Field(..., description="Database table name")
    config: Optional[Dict[str, Any]] = Field(None, description="Dataset configuration")


class DatasetCreate(DatasetBase):
    """Schema for creating a dataset"""
    pass


class DatasetUpdate(BaseModel):
    """Schema for updating a dataset"""
    name: Optional[str] = None
    description: Optional[str] = None
    config: Optional[Dict[str, Any]] = None


class DatasetResponse(DatasetBase):
    """Schema for dataset response"""
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class DataRecordCreate(BaseModel):
    """Schema for creating a data record"""
    dataset_id: int
    data: Dict[str, Any]


class DataRecordResponse(BaseModel):
    """Schema for data record response"""
    id: int
    dataset_id: int
    data: Dict[str, Any]
    created_at: datetime
    
    class Config:
        from_attributes = True


class QueryRequest(BaseModel):
    """Schema for query requests"""
    dataset: str = Field(..., description="Dataset name to query")
    filters: Optional[Dict[str, Any]] = Field(None, description="Filter conditions")
    fields: Optional[List[str]] = Field(None, description="Fields to return")
    limit: int = Field(100, ge=1, le=10000, description="Maximum number of records")
    offset: int = Field(0, ge=0, description="Number of records to skip")
    order_by: Optional[str] = Field(None, description="Field to order by")
    order_direction: str = Field("asc", description="Order direction (asc/desc)")


class QueryResponse(BaseModel):
    """Schema for query response"""
    dataset: str
    total_records: int
    returned_records: int
    data: List[Dict[str, Any]]
    query_time_ms: float
