"""
Database models for datasets and data storage
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Dataset(Base):
    """Dataset metadata model"""
    __tablename__ = "datasets"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    description = Column(Text)
    table_name = Column(String(255), unique=True, nullable=False)
    config = Column(JSON)  # Store dataset configuration
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    records = relationship("DataRecord", back_populates="dataset", cascade="all, delete-orphan")


class DataRecord(Base):
    """Generic data record model - stores actual dataset data"""
    __tablename__ = "data_records"
    
    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=False)
    data = Column(JSON, nullable=False)  # Store actual data as JSON
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Indexes for common filters
    __table_args__ = (
        Index('idx_dataset_id', 'dataset_id'),
    )
    
    # Relationships
    dataset = relationship("Dataset", back_populates="records")


class CensusData(Base):
    """Example: Census data specific model"""
    __tablename__ = "census_data"
    
    id = Column(Integer, primary_key=True, index=True)
    state = Column(String(100), index=True)
    district = Column(String(100), index=True)
    gender = Column(String(20), index=True)
    age_group = Column(String(20), index=True)
    population = Column(Integer)
    literacy_rate = Column(Float)
    employment_rate = Column(Float)
    year = Column(Integer, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Composite indexes for common query patterns
    __table_args__ = (
        Index('idx_state_gender_age', 'state', 'gender', 'age_group'),
        Index('idx_state_year', 'state', 'year'),
    )
