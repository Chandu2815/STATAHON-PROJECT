"""
Survey AI - FastAPI Backend
Modern Survey Data Explorer with Dynamic Queries
Connects exclusively to VPS PostgreSQL database
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv(verbose=True)

# Import routers
from routers.survey_data_insert import router as survey_data_router

app = FastAPI(
    title="Survey AI API",
    description="Modern Survey Data Explorer API",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(survey_data_router)

# Database Configuration - NO FALLBACK DEFAULTS (read from .env only)
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT", "5432")  # Default port only
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# Validate required configuration
missing_vars = []
if not DB_HOST:
    missing_vars.append("DB_HOST")
if not DB_NAME:
    missing_vars.append("DB_NAME")
if not DB_USER:
    missing_vars.append("DB_USER")
if not DB_PASSWORD:
    missing_vars.append("DB_PASSWORD")

if missing_vars:
    error_msg = f"❌ FATAL: Missing required environment variables: {', '.join(missing_vars)}. Please check .env file."
    logger.error(error_msg)
    raise RuntimeError(error_msg)

# Build psycopg2 config
DB_CONFIG = {
    "host": DB_HOST,
    "port": int(DB_PORT),
    "database": DB_NAME,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "connect_timeout": 10,
}

def get_db_connection():
    """Get database connection to VPS PostgreSQL"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except psycopg2.OperationalError as e:
        error_msg = f"❌ Database connection failed to {DB_HOST}:{DB_PORT}: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        error_msg = f"❌ Unexpected database error: {str(e)}"
        logger.error(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

# Test connection on startup
@app.on_event("startup")
async def startup_event():
    """Test database connection on app startup"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT version();")
        version = cur.fetchone()
        cur.close()
        conn.close()
        logger.info(f"✅ Connected to PostgreSQL at {DB_HOST}:{DB_PORT}")
        logger.info(f"✅ Database: {DB_NAME}")
        logger.info(f"✅ PostgreSQL version: {version[0][:60]}...")
        print(f"Connected DB: postgresql://{DB_USER}@{DB_HOST}:{DB_PORT}/{DB_NAME}")
    except Exception as e:
        error_msg = f"❌ FATAL: Failed to connect to VPS database on startup: {str(e)}"
        logger.error(error_msg)
        raise RuntimeError(error_msg)

# Pydantic Models
class DataRequest(BaseModel):
    table: str
    columns: List[str]
    filters: Dict[str, Any] = {}
    limit: int = 100
    offset: int = 0

# Routes

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Survey AI API is running"}

@app.get("/datasets")
async def get_datasets():
    """Get all available datasets (table names)"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Query information schema for tables in public schema and economic_census
        cur.execute("""
            SELECT schemaname, tablename FROM pg_tables 
            WHERE schemaname = 'public' OR (schemaname = 'economic_census' AND tablename = 'enterprises_full')
            UNION
            SELECT schemaname, viewname as tablename FROM pg_views
            WHERE schemaname = 'public'
            ORDER BY schemaname, tablename
        """)
        
        tables = [f"{row[0]}.{row[1]}" if row[0] != 'public' else row[1] for row in cur.fetchall()]
        cur.close()
        conn.close()
        
        return {
            "success": True,
            "datasets": tables,
            "count": len(tables)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching datasets: {str(e)}")

@app.get("/datasets/hierarchical")
async def get_datasets_hierarchical():
    """Get datasets organized in hierarchical categories"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Query all tables
        cur.execute("""
            SELECT schemaname, tablename FROM pg_tables 
            WHERE schemaname = 'public' OR (schemaname = 'economic_census' AND tablename = 'enterprises_full')
            UNION
            SELECT schemaname, viewname as tablename FROM pg_views
            WHERE schemaname = 'public'
            ORDER BY schemaname, tablename
        """)
        
        tables = [f"{row[0]}.{row[1]}" if row[0] != 'public' else row[1] for row in cur.fetchall()]
        cur.close()
        conn.close()
        
        # Organize datasets by category
        hierarchical_data = {
            "Economic Census": [],
            "HCES": [],
            "PLFS": [],
            "Survey": [],
            "Other": []
        }
        
        for table in tables:
            # Categorize by table name prefix
            if table.startswith("economic_census."):
                hierarchical_data["Economic Census"].append(table)
            elif table.startswith("hces_"):
                hierarchical_data["HCES"].append(table)
            elif table.startswith("plfs_"):
                hierarchical_data["PLFS"].append(table)
            elif table in ["person_survey", "survey_data", "census_data"]:
                hierarchical_data["Survey"].append(table)
            else:
                hierarchical_data["Other"].append(table)
        
        # Remove empty categories
        hierarchical_data = {k: v for k, v in hierarchical_data.items() if v}
        
        return {
            "success": True,
            "data": hierarchical_data,
            "total_datasets": len(tables)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching hierarchical datasets: {str(e)}")

@app.get("/columns/{table:path}")
async def get_columns(table: str):
    """Get columns for a specific table"""
    
    # Validate table name (prevent SQL injection)
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        if table.startswith("economic_census.") and any(x in table for x in ["enterprise", "raw", "parsed", "full"]):
            # Use variable metadata if available for enterprise tables
            cur.execute("""
                SELECT variable_name, data_type, description
                FROM economic_census.variable_metadata
                ORDER BY start_pos
            """)
            rows = cur.fetchall()
            if rows:
                columns = [{"name": row[0], "type": row[1], "description": row[2]} for row in rows]
            else:
                # Fallback to information_schema
                table_name = table.split(".")[1]
                cur.execute("""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_schema = 'economic_census' AND table_name = %s
                    ORDER BY ordinal_position
                """, (table_name,))
                columns = [{"name": row[0], "type": row[1]} for row in cur.fetchall()]
        else:
            # Get column information for public
            cur.execute("""
                SELECT column_name, data_type 
                FROM information_schema.columns 
                WHERE table_name = %s AND table_schema = 'public'
                ORDER BY ordinal_position
            """, (table,))
            columns = [{"name": row[0], "type": row[1]} for row in cur.fetchall()]
        
        if not columns:
            raise HTTPException(status_code=404, detail=f"Table '{table}' not found")
        
        cur.close()
        conn.close()
        
        return {
            "success": True,
            "table": table,
            "columns": columns,
            "count": len(columns)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching columns")

# Reference endpoints for UI dropdowns
@app.get("/reference/ec/states")
async def get_states():
    """Return all rows from economic_census.state_codes"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM economic_census.state_codes")
        rows = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]
        cur.close()
        conn.close()
        return {"success": True, "data": rows, "count": len(rows)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching states: {str(e)}")

@app.get("/reference/ec/districts")
async def get_districts():
    """Return all rows from economic_census.district_codes"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM economic_census.district_codes")
        rows = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]
        cur.close()
        conn.close()
        return {"success": True, "data": rows, "count": len(rows)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching districts: {str(e)}")

@app.get("/reference/ec/nic-codes")
async def get_nic_codes():
    """Return all rows from economic_census.nic_codes"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM economic_census.nic_codes")
        rows = [dict(zip([desc[0] for desc in cur.description], row)) for row in cur.fetchall()]
        cur.close()
        conn.close()
        return {"success": True, "data": rows, "count": len(rows)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching nic codes: {str(e)}")

@app.get("/distinct/{table:path}/{column}")
async def get_distinct_values(table: str, column: str):
    """Get distinct values for a specific column in a table (for filter dropdowns)"""
    # Validate inputs
    if not table.replace("_", "").replace(".", "").isalnum():
        raise HTTPException(status_code=400, detail="Invalid table name")
    if not column.replace("_", "").isalnum():
        raise HTTPException(status_code=400, detail="Invalid column name")
    
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        if "." in table:
            schema_name, table_name = table.split(".", 1)
            table_ref = f'"{schema_name}"."{table_name}"'
        else:
            table_ref = f'"{table}"'
        
        # Get distinct non-null values, ordered, with limit for performance
        cur.execute(f"""
            SELECT DISTINCT TRIM("{column}") as val
            FROM {table_ref}
            WHERE "{column}" IS NOT NULL AND TRIM("{column}") != ''
            ORDER BY val
            LIMIT 500
        """)
        
        values = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        
        return {"success": True, "data": values, "count": len(values)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching distinct values: {str(e)}")


@app.post("/data")
async def fetch_data(request: DataRequest):
    """Fetch data from database with specified columns"""
    
    conn = None
    try:
        conn = get_db_connection()
        
        # Validate table name
        if not request.table.replace("_", "").replace(".", "").isalnum():
            raise HTTPException(status_code=400, detail="Invalid table name")
        
        # Validate column names
        for col in request.columns:
            if not col.replace("_", "").isalnum():
                raise HTTPException(status_code=400, detail=f"Invalid column name: {col}")
        
        # Build safe query with properly quoted identifiers
        columns_str = ", ".join([f'"{col}"' for col in request.columns])
        
        if "." in request.table:
            schema_name, table_name = request.table.split(".", 1)
            table_ref = f'"{schema_name}"."{table_name}"'
        else:
            table_ref = f'"{request.table}"'
            
        # Build WHERE clause from filters
        where_clauses = []
        where_values = []
        
        for col, val in request.filters.items():
            if not col.replace("_", "").isalnum():
                continue
            # Use TRIM to handle padded strings in the database
            where_clauses.append(f'TRIM("{col}") = %s')
            where_values.append(str(val).strip())
            
        where_str = ""
        if where_clauses:
            where_str = " WHERE " + " AND ".join(where_clauses)
        
        # Use regular cursor to fetch data
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Query data
        query = f"SELECT {columns_str} FROM {table_ref}{where_str} LIMIT %s OFFSET %s"
        params = tuple(where_values + [int(request.limit), int(request.offset)])
        cur.execute(query, params)
        
        # Fetch as list of dicts
        rows = []
        for row in cur.fetchall():
            rows.append(dict(row))
        
        # Get total count
        count_query = f"SELECT COUNT(*) as total FROM {table_ref}{where_str}"
        cur.execute(count_query, tuple(where_values))
        total_count = cur.fetchone()["total"]
        
        cur.close()
        
        return {
            "success": True,
            "table": request.table,
            "columns": request.columns,
            "data": rows,
            "count": len(rows),
            "total": total_count,
            "limit": request.limit,
            "offset": request.offset
        }
    except HTTPException as he:
        raise he
    except Exception as e:
        print(f"❌ Error fetching data: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")
    finally:
        if conn:
            conn.close()

@app.get("/statistics/{table:path}")
async def get_statistics(table: str, column: str = None):
    """Get statistics for numeric columns"""
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        if column:
            if "." in table:
                schema_name, table_name = table.split(".", 1)
                table_ref = f'"{schema_name}"."{table_name}"'
            else:
                table_ref = f'public."{table}"'
                
            query = f"""
                SELECT 
                    COUNT(*) as total,
                    AVG("{column}") as avg,
                    MIN("{column}") as min,
                    MAX("{column}") as max,
                    STDDEV("{column}") as stddev
                FROM {table_ref}
                WHERE "{column}" IS NOT NULL
            """
            cur.execute(query)
            stats = cur.fetchone()
        else:
            stats = None
        
        cur.close()
        conn.close()
        
        return {
            "success": True,
            "table": table,
            "column": column,
            "statistics": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching statistics: {str(e)}")

@app.get("/reference/districts")
async def get_district_codes(state_code: str = None):
    """Get district codes (optionally filtered by state)"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if state_code:
            # Filter by state code
            cur.execute("""
                SELECT state_code, state_name, district_code, district_name
                FROM plfs_district_codes
                WHERE state_code = %s
                ORDER BY CAST(district_code AS INTEGER)
            """, (state_code,))
        else:
            # Get all states (for dropdown)
            cur.execute("""
                SELECT DISTINCT state_code, state_name
                FROM plfs_district_codes
                ORDER BY CAST(state_code AS INTEGER)
            """)
        
        data = cur.fetchall()
        cur.close()
        conn.close()
        
        return {
            "success": True,
            "data": data,
            "count": len(data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching district codes: {str(e)}")

@app.get("/reference/ec/states")
async def get_ec_states():
    """Get all states for Economic Census"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT state_code, state_name FROM economic_census.state_codes ORDER BY state_code")
        data = cur.fetchall()
        cur.close()
        conn.close()
        return {"success": True, "data": data, "count": len(data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching EC states: {str(e)}")

@app.get("/reference/ec/districts")
async def get_ec_districts(state_code: int = None):
    """Get districts for Economic Census"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        if state_code:
            cur.execute("SELECT district_code, district_name FROM economic_census.district_codes WHERE state_code = %s ORDER BY district_code", (state_code,))
        else:
            cur.execute("SELECT state_code, district_code, district_name FROM economic_census.district_codes ORDER BY state_code, district_code")
        data = cur.fetchall()
        cur.close()
        conn.close()
        return {"success": True, "data": data, "count": len(data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching EC districts: {str(e)}")

@app.get("/reference/ec/nic-codes")
async def get_ec_nic_codes():
    """Get NIC codes for Economic Census"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        cur.execute("SELECT nic_code, description FROM economic_census.nic_codes ORDER BY nic_code")
        data = cur.fetchall()
        cur.close()
        conn.close()
        return {"success": True, "data": data, "count": len(data)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching EC NIC codes: {str(e)}")

@app.get("/reference/states")
async def get_states():
    """Get all states with their district counts"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT state_code, state_name, COUNT(DISTINCT district_code) as district_count
            FROM plfs_district_codes
            GROUP BY state_code, state_name
            ORDER BY CAST(state_code AS INTEGER)
        """)
        
        data = cur.fetchall()
        cur.close()
        conn.close()
        
        return {
            "success": True,
            "data": data,
            "count": len(data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching states: {str(e)}")

@app.get("/reference/item-codes")
async def get_item_codes(block: str = None):
    """Get PLFS item codes (optionally filtered by block)"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if block:
            cur.execute("""
                SELECT DISTINCT block_name, item_number, item_description, code_value, code_description
                FROM plfs_item_codes
                WHERE block_name ILIKE %s
                ORDER BY item_number
            """, (f"%{block}%",))
        else:
            cur.execute("""
                SELECT DISTINCT block_name
                FROM plfs_item_codes
                ORDER BY block_name
            """)
        
        data = cur.fetchall()
        cur.close()
        conn.close()
        
        return {
            "success": True,
            "data": data,
            "count": len(data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching item codes: {str(e)}")

@app.get("/reference/metadata")
async def get_nmds_metadata():
    """Get NMDS metadata"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("""
            SELECT metadata_key, metadata_value, value_type
            FROM nmds_metadata
            ORDER BY metadata_key
        """)
        
        data = cur.fetchall()
        cur.close()
        conn.close()
        
        return {
            "success": True,
            "data": data,
            "count": len(data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching metadata: {str(e)}")

@app.get("/analytics/summary")
async def get_analytics_summary():
    """Get analytics summary across all datasets"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        
        # Get table counts
        cur.execute("""
            SELECT 
                schemaname,
                tablename,
                (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = tablename) as column_count,
                (SELECT COUNT(*) FROM information_schema.columns WHERE table_name = tablename AND data_type LIKE '%int%' OR data_type LIKE '%numeric%') as numeric_columns
            FROM pg_tables
            WHERE schemaname = 'public'
            ORDER BY tablename
        """)
        
        tables = cur.fetchall()
        summary = []
        
        for table_info in tables:
            table_name = table_info[1]
            # Get row count
            cur.execute(f'SELECT COUNT(*) FROM "{table_name}"')
            row_count = cur.fetchone()[0]
            summary.append({
                'table': table_name,
                'rows': row_count,
                'columns': table_info[2],
                'numeric_columns': table_info[3]
            })
        
        cur.close()
        conn.close()
        
        total_rows = sum(s['rows'] for s in summary)
        
        return {
            "success": True,
            "summary": summary,
            "total_tables": len(summary),
            "total_rows": total_rows
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching analytics: {str(e)}")

@app.get("/analytics/data-quality/{table:path}")
async def get_data_quality(table: str):
    """Analyze data quality for a table"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if "." in table:
            schema_name, table_name = table.split(".", 1)
            table_ref = f'"{schema_name}"."{table_name}"'
            query_schema = schema_name
            query_table = table_name
        else:
            table_ref = f'public."{table}"'
            query_schema = 'public'
            query_table = table
            
        # Get column info
        cur.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position
        """, (query_schema, query_table))
        
        columns = cur.fetchall()
        quality_metrics = []
        
        # Get total rows
        total_rows_query = f'SELECT COUNT(*) as total FROM {table_ref}'
        cur.execute(total_rows_query)
        total_result = cur.fetchone()
        total_rows = total_result['total'] if total_result else 0
        
        for col in columns:
            col_name = col['column_name']
            col_type = col['data_type']
            
            # Count nulls
            cur.execute(f'SELECT COUNT(*) as null_count FROM {table_ref} WHERE "{col_name}" IS NULL')
            null_result = cur.fetchone()
            null_count = null_result['null_count'] if null_result else 0
            
            completeness = 100 * (total_rows - null_count) / total_rows if total_rows > 0 else 0
            
            quality_metrics.append({
                'column': col_name,
                'type': col_type,
                'null_count': null_count,
                'completeness': round(completeness, 2)
            })
        
        cur.close()
        conn.close()
        
        avg_completeness = sum(m['completeness'] for m in quality_metrics) / len(quality_metrics) if quality_metrics else 0
        
        return {
            "success": True,
            "table": table,
            "total_rows": total_rows,
            "total_columns": len(quality_metrics),
            "average_completeness": round(avg_completeness, 2),
            "columns": quality_metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing data quality: {str(e)}")

@app.get("/analytics/column-distribution/{table:path}/{column}")
async def get_column_distribution(table: str, column: str):
    """Get value distribution for a column"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if "." in table:
            schema_name, table_name = table.split(".", 1)
            table_ref = f'"{schema_name}"."{table_name}"'
        else:
            table_ref = f'public."{table}"'
            
        # For categorical data - get top values
        cur.execute(f"""
            SELECT "{column}" as value, COUNT(*) as count
            FROM {table_ref}
            WHERE "{column}" IS NOT NULL
            GROUP BY "{column}"
            ORDER BY count DESC
            LIMIT 20
        """)
        
        distribution = cur.fetchall()
        cur.close()
        conn.close()
        
        return {
            "success": True,
            "table": table,
            "column": column,
            "distribution": distribution
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting distribution: {str(e)}")

@app.get("/analytics/integrity/{table:path}")
async def get_integrity_audit(table: str):
    """Detect duplicates and repeated entries in a dataset"""
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        if "." in table:
            schema_name, table_name = table.split(".", 1)
            table_ref = f'"{schema_name}"."{table_name}"'
        else:
            table_ref = f'public."{table}"'
            
        # 1. Detect Duplicate Rows (Total Count)
        # This is a generic check. In a production set, we usually check by a Unique ID if available.
        # Here we check the whole row.
        cur.execute(f'SELECT COUNT(*) as total FROM {table_ref}')
        total_rows = cur.fetchone()['total']
        
        # Get count of unique rows
        cur.execute(f'SELECT COUNT(*) FROM (SELECT DISTINCT * FROM {table_ref}) as unique_rows')
        unique_count = cur.fetchone()['count']
        
        duplicate_count = total_rows - unique_count
        
        # 2. Get specific repeated entries (Proof)
        # We'll pick the most frequent repeated rows
        cur.execute(f"""
            SELECT *, COUNT(*) as occurrence_count
            FROM {table_ref}
            GROUP BY {table_ref}.*
            HAVING COUNT(*) > 1
            ORDER BY occurrence_count DESC
            LIMIT 5
        """)
        repeated_samples = cur.fetchall()
        
        cur.close()
        conn.close()
        
        return {
            "success": True,
            "table": table,
            "integrity_score": round((unique_count / total_rows * 100), 2) if total_rows > 0 else 0,
            "duplicates_found": duplicate_count,
            "total_rows": total_rows,
            "proof_of_repetition": repeated_samples
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error performing integrity audit: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        reload=False
    )
