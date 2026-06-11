"""
Survey AI Data Explorer API endpoints
Handles filtering, distinct values, and dynamic SQL query building
"""
from fastapi import APIRouter, Depends, HTTPException, Query as QueryParam, Body
from sqlalchemy.orm import Session
from sqlalchemy import inspect, text, MetaData, Table, and_, distinct
from typing import Optional, List, Dict, Any
import json
import logging
from app.database import get_db
from app.models.user import User
from app.auth import get_current_user

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI Data Explorer"])


# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def get_table_columns(db: Session, table_name: str) -> List[Dict[str, str]]:
    """Get all columns from a table with their types"""
    try:
        inspector = inspect(db.bind)
        if table_name not in inspector.get_table_names():
            return []
        
        columns = inspector.get_columns(table_name)
        result = []
        for col in columns:
            result.append({
                'name': col['name'],
                'type': str(col['type']),
            })
        return result
    except Exception as e:
        logger.error(f"Error getting columns for {table_name}: {e}")
        return []


def get_distinct_values(db: Session, table_name: str, column_name: str, 
                       limit: int = 1000, offset: int = 0,
                       applied_filters: Optional[Dict] = None) -> List[Any]:
    """
    Get distinct values for a column, optionally filtered by other selected values
    """
    try:
        # Validate table exists
        inspector = inspect(db.bind)
        if table_name not in inspector.get_table_names():
            logger.error(f"Table {table_name} not found")
            return []
        
        # Build query with applied filters
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=db.bind)
        
        query = db.query(distinct(getattr(table.c, column_name)))
        
        # Apply existing filters if provided
        if applied_filters:
            for filter_col, filter_val in applied_filters.items():
                if filter_col != column_name and hasattr(table.c, filter_col):
                    try:
                        query = query.filter(getattr(table.c, filter_col) == filter_val)
                    except Exception as e:
                        logger.debug(f"Could not apply filter {filter_col}={filter_val}: {e}")
        
        # Get distinct values
        results = query.order_by(getattr(table.c, column_name)).limit(limit).offset(offset).all()
        
        # Convert to list of values
        values = [row[0] for row in results if row[0] is not None]
        
        logger.debug(f"Got {len(values)} distinct values for {table_name}.{column_name}")
        return values
        
    except Exception as e:
        logger.error(f"Error getting distinct values for {table_name}.{column_name}: {e}")
        return []


def build_filter_conditions(db: Session, table_name: str, filters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build WHERE conditions from filter dictionary
    Handles different data types automatically
    """
    try:
        metadata = MetaData()
        table = Table(table_name, metadata, autoload_with=db.bind)
        
        conditions = {}
        for col_name, value in filters.items():
            if not value or value == '':
                continue
                
            if hasattr(table.c, col_name):
                # Auto-convert based on column type
                col_type = str(table.c[col_name].type)
                
                try:
                    if 'INT' in col_type.upper():
                        conditions[col_name] = int(value)
                    elif 'FLOAT' in col_type.upper() or 'NUMERIC' in col_type.upper():
                        conditions[col_name] = float(value)
                    else:
                        conditions[col_name] = str(value)
                except ValueError:
                    conditions[col_name] = str(value)
                
                logger.debug(f"Filter: {col_name} = {conditions[col_name]} (type: {col_type})")
        
        return conditions
    except Exception as e:
        logger.error(f"Error building filter conditions: {e}")
        return {}


# ═══════════════════════════════════════════════════════════════════════════
# PUBLIC API ENDPOINTS
# ═══════════════════════════════════════════════════════════════════════════

@router.get("/datasets/hierarchical")
async def get_hierarchical_datasets(db: Session = Depends(get_db)):
    """
    Get all available datasets organized hierarchically
    This is a public endpoint for dataset discovery
    """
    try:
        inspector = inspect(db.bind)
        all_tables = inspector.get_table_names()
        
        # Filter for survey tables
        survey_tables = [t for t in all_tables if any(keyword in t.lower() for keyword in 
                         ['survey', 'plfs', 'census', 'household', 'person', 'enterprise', 'hces'])]
        
        datasets = {}
        for table in sorted(survey_tables):
            try:
                # Get row count
                count_result = db.execute(text(f"SELECT COUNT(*) FROM \"{table}\""))
                row_count = count_result.scalar() or 0
                
                # Get column count
                columns = inspector.get_columns(table)
                col_count = len(columns)
                
                # Organize by category
                if 'household' in table.lower():
                    category = 'Household Surveys'
                elif 'person' in table.lower():
                    category = 'Person Surveys'
                elif 'enterprise' in table.lower():
                    category = 'Enterprise Surveys'
                elif 'hces' in table.lower():
                    category = 'HCES Data'
                else:
                    category = 'Other Surveys'
                
                if category not in datasets:
                    datasets[category] = []
                
                datasets[category].append({
                    'name': table,
                    'display_name': table.replace('_', ' ').title(),
                    'row_count': row_count,
                    'column_count': col_count,
                })
            except Exception as e:
                logger.debug(f"Error processing table {table}: {e}")
        
        return {
            'success': True,
            'data': datasets,
            'total_datasets': len(survey_tables)
        }
    except Exception as e:
        logger.error(f"Error fetching hierarchical datasets: {e}")
        return {
            'success': False,
            'error': str(e),
            'data': {}
        }


@router.get("/columns/{dataset}")
async def get_dataset_columns(
    dataset: str,
    db: Session = Depends(get_db)
):
    """
    Get all columns for a dataset
    """
    try:
        columns = get_table_columns(db, dataset)
        if not columns:
            return {
                'success': False,
                'error': f"Dataset '{dataset}' not found",
                'columns': []
            }
        
        logger.info(f"Retrieved {len(columns)} columns for dataset {dataset}")
        return {
            'success': True,
            'columns': columns,
            'total': len(columns)
        }
    except Exception as e:
        logger.error(f"Error getting columns for {dataset}: {e}")
        return {
            'success': False,
            'error': str(e),
            'columns': []
        }


@router.get("/distinct/{dataset}/{column}")
async def get_distinct_column_values(
    dataset: str,
    column: str,
    limit: int = QueryParam(100, ge=1, le=10000),
    offset: int = QueryParam(0, ge=0),
    filters: Optional[str] = QueryParam(None),
    db: Session = Depends(get_db)
):
    """
    Get distinct values for a column
    Optionally filtered by other selected filter values
    
    Example: /ai/distinct/household_survey/state_code?filters={"district_code": "28"}
    """
    try:
        # Parse applied filters if provided
        applied_filters = {}
        if filters:
            try:
                applied_filters = json.loads(filters)
            except:
                pass
        
        values = get_distinct_values(db, dataset, column, limit, offset, applied_filters)
        
        logger.debug(f"Distinct values for {dataset}.{column}: {len(values)} records")
        
        return {
            'success': True,
            'data': values,
            'total': len(values),
            'column': column,
            'dataset': dataset
        }
    except Exception as e:
        logger.error(f"Error getting distinct values: {e}")
        return {
            'success': False,
            'error': str(e),
            'data': []
        }


@router.post("/data")
async def query_data_with_filters(
    body: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db)
):
    """
    Query data from a table with applied filters
    Supports cascading filters and returns filtered results
    
    Request body:
    {
        "table": "household_survey",
        "columns": ["state_code", "district_code", "ownership_type"],
        "filters": {
            "state_code": 28,
            "district_code": 1
        },
        "limit": 100,
        "offset": 0
    }
    """
    try:
        table = body.get('table')
        columns = body.get('columns', [])
        filters = body.get('filters', {})
        limit = min(int(body.get('limit', 100)), 10000)
        offset = int(body.get('offset', 0))

        logger.info(f"[QUERY REQUEST] Table={table}, Columns={columns}, Filters={filters}, Limit={limit}, Offset={offset}")
        
        if not table:
            return {
                'success': False,
                'error': 'Missing required parameter: table',
                'data': [],
                'total': 0
            }
        
        if not columns:
            return {
                'success': False,
                'error': 'Missing required parameter: columns',
                'data': [],
                'total': 0
            }
        
        # Validate table exists
        inspector = inspect(db.bind)
        if table not in inspector.get_table_names():
            return {
                'success': False,
                'error': f"Table '{table}' not found",
                'data': [],
                'total': 0
            }
        
        # Validate all columns exist
        available_columns = [col['name'] for col in get_table_columns(db, table)]
        for col in columns:
            if col not in available_columns:
                return {
                    'success': False,
                    'error': f"Column '{col}' not found in table '{table}'",
                    'data': [],
                    'total': 0,
                    'available_columns': available_columns
                }
        
        # Build query
        metadata = MetaData()
        db_table = Table(table, metadata, autoload_with=db.bind)
        
        # Select only requested columns
        query = db.query(*[getattr(db_table.c, col) for col in columns])
        
        # Apply filters
        filter_conditions = build_filter_conditions(db, table, filters)
        for col_name, value in filter_conditions.items():
            if hasattr(db_table.c, col_name):
                query = query.filter(getattr(db_table.c, col_name) == value)
        
        # Get total count
        total = query.count()

        # Apply pagination
        results = query.limit(limit).offset(offset).all()

        # Convert to list of dicts
        data = []
        for row in results:
            row_dict = {}
            for i, col in enumerate(columns):
                row_dict[col] = row[i]
            data.append(row_dict)

        logger.info(f"[QUERY SUCCESS] Returned {len(data)} records out of {total} matching filter conditions. Filters applied: {filter_conditions}")
        
        return {
            'success': True,
            'data': data,
            'total': total,
            'limit': limit,
            'offset': offset,
            'filters_applied': filter_conditions,
            'message': f"Fetched {len(data)} records out of {total} total"
        }
        
    except Exception as e:
        logger.error(f"Error querying data: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
            'data': [],
            'total': 0
        }


@router.get("/reference/states")
async def get_states(db: Session = Depends(get_db)):
    """Get all available states"""
    try:
        # Try to get states from a reference table or query distinct from survey tables
        states = []
        
        # Query from any table with state information
        inspector = inspect(db.bind)
        all_tables = inspector.get_table_names()
        
        for table in all_tables:
            if 'survey' in table.lower() or 'census' in table.lower():
                try:
                    # Try different state column name variants
                    for col_name in ['state_code', 'State_Code', 'State_UT_Code']:
                        if any(col['name'] == col_name for col in inspector.get_columns(table)):
                            metadata = MetaData()
                            db_table = Table(table, metadata, autoload_with=db.bind)
                            state_query = db.query(distinct(getattr(db_table.c, col_name))).order_by(getattr(db_table.c, col_name))
                            for (state_code,) in state_query.limit(37).all():
                                if state_code is not None:
                                    states.append({
                                        'state_code': state_code,
                                        'state_name': f'State {state_code}'  # You can enhance this with a mapping
                                    })
                            break
                    
                    if states:
                        break
                except:
                    continue
        
        return {
            'success': True,
            'data': states,
            'total': len(states)
        }
    except Exception as e:
        logger.error(f"Error getting states: {e}")
        return {
            'success': False,
            'error': str(e),
            'data': []
        }


@router.get("/reference/districts")
async def get_districts(
    state_code: Optional[str] = QueryParam(None),
    db: Session = Depends(get_db)
):
    """Get all available districts, optionally filtered by state"""
    try:
        districts = []
        inspector = inspect(db.bind)
        all_tables = inspector.get_table_names()
        
        for table in all_tables:
            if 'survey' in table.lower() or 'census' in table.lower():
                try:
                    for col_name in ['district_code', 'District_Code']:
                        if any(col['name'] == col_name for col in inspector.get_columns(table)):
                            metadata = MetaData()
                            db_table = Table(table, metadata, autoload_with=db.bind)
                            
                            query = db.query(distinct(getattr(db_table.c, col_name)))
                            
                            # Filter by state if provided
                            if state_code:
                                for state_col_name in ['state_code', 'State_Code', 'State_UT_Code']:
                                    if any(col['name'] == state_col_name for col in inspector.get_columns(table)):
                                        query = query.filter(getattr(db_table.c, state_col_name) == state_code)
                                        break
                            
                            district_query = query.order_by(getattr(db_table.c, col_name))
                            for (district_code,) in district_query.limit(1000).all():
                                if district_code is not None:
                                    districts.append({
                                        'district_code': district_code,
                                        'district_name': f'District {district_code}',
                                        'state_code': state_code
                                    })
                            break
                    
                    if districts:
                        break
                except:
                    continue
        
        return {
            'success': True,
            'data': districts,
            'total': len(districts)
        }
    except Exception as e:
        logger.error(f"Error getting districts: {e}")
        return {
            'success': False,
            'error': str(e),
            'data': []
        }


@router.get("/reference/ec/states")
async def get_economic_census_states(db: Session = Depends(get_db)):
    """Get all available states from economic census data"""
    try:
        states = []
        inspector = inspect(db.bind)
        all_tables = inspector.get_table_names()

        for table in all_tables:
            if 'economic_census' in table.lower():
                try:
                    for col_name in ['state_code', 'State_Code', 'State_UT_Code']:
                        if any(col['name'] == col_name for col in inspector.get_columns(table)):
                            metadata = MetaData()
                            db_table = Table(table, metadata, autoload_with=db.bind)
                            state_query = db.query(distinct(getattr(db_table.c, col_name))).order_by(getattr(db_table.c, col_name))
                            for (state_code,) in state_query.limit(37).all():
                                if state_code is not None:
                                    states.append({
                                        'state_code': state_code,
                                        'state_name': f'State {state_code}'
                                    })
                            break

                    if states:
                        break
                except:
                    continue

        logger.debug(f"Economic census states: {len(states)} records")
        return {
            'success': True,
            'data': states,
            'total': len(states)
        }
    except Exception as e:
        logger.error(f"Error getting economic census states: {e}")
        return {
            'success': False,
            'error': str(e),
            'data': []
        }


@router.get("/reference/ec/districts")
async def get_economic_census_districts(
    state_code: Optional[str] = QueryParam(None),
    db: Session = Depends(get_db)
):
    """Get all available districts from economic census data, optionally filtered by state"""
    try:
        districts = []
        inspector = inspect(db.bind)
        all_tables = inspector.get_table_names()

        for table in all_tables:
            if 'economic_census' in table.lower():
                try:
                    for col_name in ['district_code', 'District_Code']:
                        if any(col['name'] == col_name for col in inspector.get_columns(table)):
                            metadata = MetaData()
                            db_table = Table(table, metadata, autoload_with=db.bind)

                            query = db.query(distinct(getattr(db_table.c, col_name)))

                            if state_code:
                                for state_col_name in ['state_code', 'State_Code', 'State_UT_Code']:
                                    if any(col['name'] == state_col_name for col in inspector.get_columns(table)):
                                        query = query.filter(getattr(db_table.c, state_col_name) == state_code)
                                        break

                            district_query = query.order_by(getattr(db_table.c, col_name))
                            for (district_code,) in district_query.limit(1000).all():
                                if district_code is not None:
                                    districts.append({
                                        'district_code': district_code,
                                        'district_name': f'District {district_code}',
                                        'state_code': state_code
                                    })
                            break

                    if districts:
                        break
                except:
                    continue

        logger.debug(f"Economic census districts for state {state_code}: {len(districts)} records")
        return {
            'success': True,
            'data': districts,
            'total': len(districts)
        }
    except Exception as e:
        logger.error(f"Error getting economic census districts: {e}")
        return {
            'success': False,
            'error': str(e),
            'data': []
        }



async def get_dataset_statistics(
    dataset: str,
    filters: Optional[str] = QueryParam(None),
    db: Session = Depends(get_db)
):
    """Get basic statistics for a dataset"""
    try:
        inspector = inspect(db.bind)
        if dataset not in inspector.get_table_names():
            return {
                'success': False,
                'error': f"Dataset '{dataset}' not found",
                'statistics': {}
            }
        
        # Parse filters
        applied_filters = {}
        if filters:
            try:
                applied_filters = json.loads(filters)
            except:
                pass
        
        # Get total count
        metadata = MetaData()
        db_table = Table(dataset, metadata, autoload_with=db.bind)
        query = db.query(db_table)
        
        # Apply filters
        for col_name, value in applied_filters.items():
            if hasattr(db_table.c, col_name):
                query = query.filter(getattr(db_table.c, col_name) == value)
        
        total_count = query.count()
        
        columns = get_table_columns(db, dataset)
        
        return {
            'success': True,
            'statistics': {
                'total_records': total_count,
                'total_columns': len(columns),
                'dataset_name': dataset
            }
        }
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return {
            'success': False,
            'error': str(e),
            'statistics': {}
        }
