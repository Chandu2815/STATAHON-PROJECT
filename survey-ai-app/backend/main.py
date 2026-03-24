"""
Survey AI - FastAPI Backend
Modern Survey Data Explorer with Dynamic Queries
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv

load_dotenv()

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

# Database Configuration
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "127.0.0.1"),
    "port": os.getenv("DB_PORT", 5432),
    "database": os.getenv("DB_NAME", "survey_db"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "1234"),
}

def get_db_connection():
    """Get database connection"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

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
        
        # Query information schema for tables in public schema
        cur.execute("""
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            ORDER BY tablename
        """)
        
        tables = [row[0] for row in cur.fetchall()]
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
            SELECT tablename FROM pg_tables 
            WHERE schemaname = 'public' 
            ORDER BY tablename
        """)
        
        tables = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        
        # Organize datasets by category
        hierarchical_data = {
            "HCES": [],
            "PLFS": [],
            "Survey": [],
            "Other": []
        }
        
        for table in tables:
            # Categorize by table name prefix
            if table.startswith("hces_"):
                hierarchical_data["HCES"].append(table)
            elif table.startswith("plfs_"):
                hierarchical_data["PLFS"].append(table)
            elif table in ["person_survey", "survey_data"]:
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

@app.get("/columns/{table}")
async def get_columns(table: str):
    """Get columns for a specific table"""
    
    # Validate table name (prevent SQL injection)
    conn = get_db_connection()
    cur = conn.cursor()
    
    try:
        # Get column information
        cur.execute(f"""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = %s
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
        raise HTTPException(status_code=500, detail=f"Error fetching columns: {str(e)}")

@app.post("/data")
async def fetch_data(request: DataRequest):
    """Fetch data from database with specified columns"""
    
    conn = None
    try:
        conn = get_db_connection()
        
        # Validate table name
        if not request.table.replace("_", "").isalnum():
            raise HTTPException(status_code=400, detail="Invalid table name")
        
        # Validate column names
        for col in request.columns:
            if not col.replace("_", "").isalnum():
                raise HTTPException(status_code=400, detail=f"Invalid column name: {col}")
        
        # Build safe query with properly quoted identifiers
        columns_str = ", ".join([f'"{col}"' for col in request.columns])
        table_name = f'"{request.table}"'
        
        # Use regular cursor to fetch data
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Query data
        query = f"SELECT {columns_str} FROM {table_name} LIMIT %s OFFSET %s"
        cur.execute(query, (int(request.limit), int(request.offset)))
        
        # Fetch as list of dicts
        rows = []
        for row in cur.fetchall():
            rows.append(dict(row))
        
        # Get total count
        count_query = f"SELECT COUNT(*) as total FROM {table_name}"
        cur.execute(count_query)
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

@app.get("/statistics/{table}")
async def get_statistics(table: str, column: str = None):
    """Get statistics for numeric columns"""
    
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        if column:
            query = f"""
                SELECT 
                    COUNT(*) as total,
                    AVG("{column}") as avg,
                    MIN("{column}") as min,
                    MAX("{column}") as max,
                    STDDEV("{column}") as stddev
                FROM public.{table}
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        reload=True
    )
