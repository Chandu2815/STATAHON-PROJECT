"""
Query builder service for dynamic database queries
"""
from typing import Dict, Any, List, Optional
from sqlalchemy import and_, or_, desc, asc
from sqlalchemy.orm import Session
from app.models import CensusData, DataRecord, Dataset
import time


class QueryBuilderService:
    """Service for building and executing dynamic queries"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def build_census_query(
        self,
        filters: Optional[Dict[str, Any]] = None,
        fields: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0,
        order_by: Optional[str] = None,
        order_direction: str = "asc"
    ):
        """Build query for census data with filters"""
        
        # Start with base query
        query = self.db.query(CensusData)
        
        # Apply filters
        if filters:
            conditions = []
            
            for field, value in filters.items():
                if hasattr(CensusData, field):
                    column = getattr(CensusData, field)
                    
                    # Handle different filter types
                    if isinstance(value, list):
                        # IN clause for lists
                        conditions.append(column.in_(value))
                    elif isinstance(value, dict):
                        # Range queries
                        if 'min' in value:
                            conditions.append(column >= value['min'])
                        if 'max' in value:
                            conditions.append(column <= value['max'])
                    else:
                        # Exact match
                        conditions.append(column == value)
            
            if conditions:
                query = query.filter(and_(*conditions))
        
        # Get total count before pagination
        total_count = query.count()
        
        # Apply ordering
        if order_by and hasattr(CensusData, order_by):
            order_column = getattr(CensusData, order_by)
            if order_direction.lower() == "desc":
                query = query.order_by(desc(order_column))
            else:
                query = query.order_by(asc(order_column))
        
        # Apply pagination
        query = query.limit(limit).offset(offset)
        
        return query, total_count
    
    def execute_census_query(
        self,
        filters: Optional[Dict[str, Any]] = None,
        fields: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0,
        order_by: Optional[str] = None,
        order_direction: str = "asc"
    ) -> Dict[str, Any]:
        """Execute census query and return results"""
        
        start_time = time.time()
        
        query, total_count = self.build_census_query(
            filters, fields, limit, offset, order_by, order_direction
        )
        
        # Execute query
        results = query.all()
        
        # Convert to dictionaries
        data = []
        for record in results:
            record_dict = {
                'id': record.id,
                'state': record.state,
                'district': record.district,
                'gender': record.gender,
                'age_group': record.age_group,
                'population': record.population,
                'literacy_rate': record.literacy_rate,
                'employment_rate': record.employment_rate,
                'year': record.year
            }
            
            # Filter fields if specified
            if fields:
                record_dict = {k: v for k, v in record_dict.items() if k in fields}
            
            data.append(record_dict)
        
        query_time = (time.time() - start_time) * 1000  # Convert to milliseconds
        
        return {
            'dataset': 'census',
            'total_records': total_count,
            'returned_records': len(data),
            'data': data,
            'query_time_ms': round(query_time, 2)
        }
    
    def execute_generic_query(
        self,
        dataset_name: str,
        filters: Optional[Dict[str, Any]] = None,
        fields: Optional[List[str]] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict[str, Any]:
        """Execute query on generic data records"""
        
        start_time = time.time()
        
        # Get dataset
        dataset = self.db.query(Dataset).filter(Dataset.name == dataset_name).first()
        if not dataset:
            raise ValueError(f"Dataset '{dataset_name}' not found")
        
        # Build query
        query = self.db.query(DataRecord).filter(DataRecord.dataset_id == dataset.id)
        
        # Note: Filtering JSON data in PostgreSQL requires different approach
        # This is a simplified version
        total_count = query.count()
        
        # Apply pagination
        query = query.limit(limit).offset(offset)
        results = query.all()
        
        # Extract data
        data = [record.data for record in results]
        
        # Apply field filtering if specified
        if fields:
            data = [
                {k: v for k, v in record.items() if k in fields}
                for record in data
            ]
        
        query_time = (time.time() - start_time) * 1000
        
        return {
            'dataset': dataset_name,
            'total_records': total_count,
            'returned_records': len(data),
            'data': data,
            'query_time_ms': round(query_time, 2)
        }
