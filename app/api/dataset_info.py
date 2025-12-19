"""
Dataset information and exploration endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from app.database import get_db
from app.auth import get_current_user
from app.models.user import User
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/datasets", tags=["Dataset Information"])


@router.get("/info")
def get_datasets_info(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive information about all uploaded PLFS datasets
    
    Shows what each dataset contains, structure, and sample data.
    Data source: microdata.gov.in (PLFS Panel 4, 2023-24)
    
    **Returns:**
    - Summary of all 3 datasets
    - Field descriptions
    - Sample records
    - Statistics and coverage
    - API endpoints for each dataset
    """
    try:
        from app.models.dataset import PLFSData
        
        # Get all unique datasets
        datasets_raw = db.query(
            PLFSData.dataset_name,
            func.count(PLFSData.id).label('count')
        ).group_by(PLFSData.dataset_name).all()
        
        datasets_info = []
        
        for dataset in datasets_raw:
            # Get sample records
            samples = db.query(PLFSData).filter(
                PLFSData.dataset_name == dataset.dataset_name
            ).limit(3).all()
            
            if dataset.dataset_name == "District_codes_PLFS":
                # Extract unique states
                all_records = db.query(PLFSData).filter(
                    PLFSData.dataset_name == dataset.dataset_name
                ).all()
                
                states = set()
                for r in all_records:
                    if 'Unnamed: 1' in r.data:
                        states.add(r.data['Unnamed: 1'])
                
                datasets_info.append({
                    "id": "plfs_district_codes",
                    "name": "PLFS District Codes",
                    "description": "Complete mapping of Indian districts with NSS (National Sample Survey) codes",
                    "source_file": "District_codes_PLFS_Panel_4_202324_2024 (1).xlsx",
                    "source": "microdata.gov.in - PLFS Panel 4 (2023-24)",
                    "total_records": dataset.count,
                    "contains": {
                        "states": len(states),
                        "districts": dataset.count,
                        "geographic_coverage": "All India"
                    },
                    "fields": [
                        {
                            "name": "state",
                            "column": "Unnamed: 1",
                            "type": "string",
                            "description": "State name (uppercase)",
                            "example": samples[0].data.get('Unnamed: 1') if samples else None
                        },
                        {
                            "name": "nss_code",
                            "column": "Unnamed: 2",
                            "type": "integer",
                            "description": "NSS district code (unique identifier)",
                            "example": samples[0].data.get('Unnamed: 2') if samples else None
                        },
                        {
                            "name": "district",
                            "column": "Unnamed: 3",
                            "type": "string",
                            "description": "District name",
                            "example": samples[0].data.get('Unnamed: 3') if samples else None
                        }
                    ],
                    "sample_data": [
                        {
                            "state": s.data.get('Unnamed: 1'),
                            "nss_code": s.data.get('Unnamed: 2'),
                            "district": s.data.get('Unnamed: 3')
                        } for s in samples
                    ],
                    "use_cases": [
                        "Filter data by state or district",
                        "NSS code lookup for survey data",
                        "Geographic analysis and mapping",
                        "Regional data aggregation"
                    ],
                    "api_endpoint": "/api/v1/plfs/district-codes"
                })
                
            elif dataset.dataset_name == "PLFS_Data_Layout":
                # Get unique blocks
                all_records = db.query(PLFSData).filter(
                    PLFSData.dataset_name == dataset.dataset_name
                ).all()
                
                blocks = set()
                for r in all_records:
                    if r.sheet:
                        blocks.add(r.sheet)
                
                datasets_info.append({
                    "id": "plfs_data_layout",
                    "name": "PLFS Data Layout",
                    "description": "Survey structure showing all variables, their positions, and definitions",
                    "source_file": "Data_LayoutPLFS_Calendar_2024 (4).xlsx",
                    "source": "microdata.gov.in - PLFS Panel 4 (2023-24) Technical Documentation",
                    "total_records": dataset.count,
                    "contains": {
                        "blocks": len(blocks),
                        "variables": dataset.count,
                        "documentation": "Variable definitions and survey structure"
                    },
                    "fields": [
                        {
                            "name": "block_description",
                            "column": "Unnamed: 1",
                            "type": "string",
                            "description": "Survey block/section description",
                            "example": samples[0].data.get('Unnamed: 1') if samples else None
                        },
                        {
                            "name": "item_code",
                            "column": "Unnamed: 3",
                            "type": "string",
                            "description": "Variable code identifier",
                            "example": samples[0].data.get('Unnamed: 3') if samples else None
                        },
                        {
                            "name": "sheet",
                            "type": "string",
                            "description": "Block number or section name",
                            "example": samples[0].sheet if samples else None
                        }
                    ],
                    "sample_data": [
                        {
                            "block": s.sheet,
                            "description": s.data.get('Unnamed: 1'),
                            "code": s.data.get('Unnamed: 3')
                        } for s in samples
                    ],
                    "use_cases": [
                        "Understand survey questionnaire structure",
                        "Variable definitions and descriptions",
                        "Data dictionary for analysis",
                        "Survey documentation reference"
                    ],
                    "api_endpoint": "/api/v1/plfs/data-layout"
                })
                
            elif dataset.dataset_name == "PLFS_Item_Codes":
                # Get unique blocks
                all_records = db.query(PLFSData).filter(
                    PLFSData.dataset_name == dataset.dataset_name
                ).all()
                
                blocks = set()
                for r in all_records:
                    if r.sheet:
                        blocks.add(r.sheet)
                
                datasets_info.append({
                    "id": "plfs_item_codes",
                    "name": "PLFS Item Codes",
                    "description": "Complete codebook with all response categories and value labels",
                    "source_file": "PLFS Panel 4 Sch 10.4 Item Code Description & Codes (1).xlsx",
                    "source": "microdata.gov.in - PLFS Panel 4 (2023-24) Codebook",
                    "total_records": dataset.count,
                    "contains": {
                        "blocks": len(blocks),
                        "survey_items": dataset.count,
                        "coding_scheme": "Response categories and value labels for all questions"
                    },
                    "fields": [
                        {
                            "name": "item_description",
                            "column": "Unnamed: 1",
                            "type": "string",
                            "description": "Survey item/question description",
                            "example": samples[0].data.get('Unnamed: 1') if samples else None
                        },
                        {
                            "name": "code",
                            "column": "Unnamed: 3",
                            "type": "string",
                            "description": "Response code/value",
                            "example": samples[0].data.get('Unnamed: 3') if samples else None
                        },
                        {
                            "name": "block",
                            "type": "string",
                            "description": "Survey block (section number)",
                            "example": samples[0].sheet if samples else None
                        }
                    ],
                    "sample_data": [
                        {
                            "block": s.sheet,
                            "item": s.data.get('Unnamed: 1'),
                            "code": s.data.get('Unnamed: 3')
                        } for s in samples
                    ],
                    "use_cases": [
                        "Lookup response category meanings",
                        "Data validation and cleaning",
                        "Value label mapping",
                        "Survey codebook reference"
                    ],
                    "api_endpoint": "/api/v1/plfs/item-codes"
                })
        
        total_records = sum(d['total_records'] for d in datasets_info)
        
        return {
            "summary": {
                "total_datasets": len(datasets_info),
                "total_records": total_records,
                "data_source": "microdata.gov.in",
                "survey_name": "Periodic Labour Force Survey (PLFS)",
                "survey_period": "Panel 4 (2023-2024)",
                "geographic_coverage": "All India - States and Districts",
                "data_quality": "Official Government Statistics - Ministry of Statistics and Programme Implementation"
            },
            "datasets": datasets_info,
            "how_to_query": {
                "filter_by_state": "GET /api/v1/plfs/district-codes?state=MAHARASHTRA",
                "filter_by_block": "GET /api/v1/plfs/item-codes?block_no=3",
                "export_csv": "GET /api/v1/export/csv?dataset=plfs_districts&limit=100",
                "visualize_chart": "GET /api/v1/export/chart?dataset=usage&x_field=date&y_field=requests",
                "visualize_table": "GET /api/v1/export/table?dataset=plfs_districts&limit=50"
            },
            "available_filters": {
                "state": "Filter by state name",
                "district": "Filter by district name",
                "block_no": "Filter by survey block number",
                "keyword": "Search by keyword in descriptions",
                "limit": "Maximum records to return",
                "skip": "Records to skip (pagination)"
            }
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve dataset info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve dataset information: {str(e)}"
        )


@router.get("/summary")
def get_datasets_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Quick summary of all datasets
    
    Returns basic counts and statistics without detailed field information.
    Faster than /info endpoint for dashboard displays.
    """
    try:
        from app.models.dataset import PLFSData
        
        datasets = db.query(
            PLFSData.dataset_name,
            func.count(PLFSData.id).label('count')
        ).group_by(PLFSData.dataset_name).all()
        
        dataset_map = {
            "District_codes_PLFS": "District Codes (695 records)",
            "PLFS_Data_Layout": "Data Layout (400 records)",
            "PLFS_Item_Codes": "Item Codes (377 records)"
        }
        
        return {
            "total_datasets": len(datasets),
            "total_records": sum(d.count for d in datasets),
            "datasets": [
                {
                    "name": dataset_map.get(d.dataset_name, d.dataset_name),
                    "id": d.dataset_name,
                    "records": d.count
                } for d in datasets
            ],
            "source": "microdata.gov.in - PLFS Panel 4 (2023-24)"
        }
        
    except Exception as e:
        logger.error(f"Failed to retrieve dataset summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve dataset summary"
        )
