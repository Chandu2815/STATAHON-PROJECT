"""
Survey AI Data Explorer API endpoints
Handles filtering, distinct values, and dynamic SQL query building
"""
from fastapi import APIRouter, Depends, HTTPException, Query as QueryParam, Body
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import inspect, text, MetaData, Table, and_, distinct
from typing import Optional, List, Dict, Any
import json
import logging
import time
from app.database import get_db, SessionLocal
from app.models.user import User
from app.auth import get_current_user

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["AI Data Explorer"])

SYSTEM_SCHEMAS = {"information_schema", "pg_catalog", "pg_toast"}
PREFERRED_SCHEMA_ORDER = {"public": 0, "economic_census": 1, "plfs": 2}
EC_ENTERPRISES_DATASET = "economic_census.enterprises_full"
EC_TECHNICAL_PATTERNS = (
    "id",
    "_id",
    "sno",
    "serial",
    "enumeration_block",
    "additional_eb",
    "file_code",
    "timestamp",
    "created_at",
    "updated_at",
    "metadata",
    "start_pos",
    "end_pos",
    "record_length",
)
EC_FILTERS = [
    {
        "name": "state_code",
        "label": "State",
        "lookup": "economic_census.state_codes",
        "value_column": "state_code",
        "label_column": "state_name",
        "cascades_to": ["district_code"],
    },
    {
        "name": "district_code",
        "label": "District",
        "lookup": "economic_census.district_codes",
        "value_column": "district_code",
        "label_column": "district_name",
        "depends_on": "state_code",
    },
    {
        "name": "major_activity_code",
        "label": "Activity Category",
        "lookup": "economic_census.variable_metadata",
        "value_column": "major_activity_code",
        "label_column": None,
        "cascades_to": ["activity_code"],
    },
    {
        "name": "activity_code",
        "label": "Activity/NIC",
        "lookup": "economic_census.nic_codes",
        "value_column": "nic_code",
        "label_column": "description",
        "depends_on": "major_activity_code",
    },
    {"name": "sector", "label": "Sector"},
    {"name": "ownership_type", "label": "Ownership"},
    {"name": "enterprise_classification", "label": "Enterprise Type"},
    {"name": "social_group_owner", "label": "Social Group"},
]


def _is_ec_enterprises(dataset: str) -> bool:
    return dataset.lower() == EC_ENTERPRISES_DATASET


def _is_hidden_ec_column(column_name: str) -> bool:
    lower = column_name.lower()
    return any(pattern == lower or pattern in lower for pattern in EC_TECHNICAL_PATTERNS)


def _humanize_column_name(column_name: str) -> str:
    overrides = {
        "state_code": "State",
        "district_code": "District",
        "activity_code": "Activity/NIC",
        "major_activity_code": "Activity Category",
        "ownership_type": "Ownership",
        "enterprise_classification": "Enterprise Type",
        "social_group_owner": "Social Group",
    }
    return overrides.get(column_name, column_name.replace("_", " ").title())


def _ec_column_metadata(db: Session) -> Dict[str, Dict[str, Any]]:
    try:
        rows = db.execute(
            text(
                """
                SELECT variable_name, description
                FROM economic_census.variable_metadata
                """
            )
        ).fetchall()
        return {row[0]: {"description": row[1]} for row in rows}
    except Exception as exc:
        logger.debug(f"[ec metadata] Could not load variable metadata: {exc}")
        return {}


def _ec_mapping_for_column(column_name: str) -> Optional[Dict[str, str]]:
    mappings = {
        "state_code": {
            "lookup_table": "economic_census.state_codes",
            "join": "enterprises_full.state_code = state_codes.state_code",
            "label_column": "state_name",
        },
        "district_code": {
            "lookup_table": "economic_census.district_codes",
            "join": "enterprises_full.state_code = district_codes.state_code AND enterprises_full.district_code = district_codes.district_code",
            "label_column": "district_name",
        },
        "activity_code": {
            "lookup_table": "economic_census.nic_codes",
            "join": "enterprises_full.activity_code = nic_codes.nic_code",
            "label_column": "description",
        },
    }
    if column_name in mappings:
        return mappings[column_name]
    if column_name.endswith("_code") or column_name in {"sector", "ownership_type", "enterprise_classification", "social_group_owner"}:
        return {
            "lookup_table": "economic_census.variable_metadata",
            "join": f"metadata definition for {column_name}",
            "label_column": "description",
        }
    return None


def _ec_ux_profile(db: Session, columns: List[Dict[str, str]]) -> Dict[str, Any]:
    metadata = _ec_column_metadata(db)
    mapped_columns = []
    hidden_columns = []
    enriched_columns = []
    available = {col["name"] for col in columns}
    filter_list = [flt for flt in EC_FILTERS if flt["name"] in available]

    for col in columns:
        name = col["name"]
        mapping = _ec_mapping_for_column(name)
        hidden = _is_hidden_ec_column(name)
        if mapping:
            mapped_columns.append({"column": name, **mapping})
        if hidden:
            hidden_columns.append(name)
        enriched_columns.append({
            **col,
            "label": _humanize_column_name(name),
            "description": metadata.get(name, {}).get("description"),
            "hidden": hidden,
            "coded": bool(mapping),
            "mapping": mapping,
        })

    return {
        "columns": enriched_columns,
        "mapped_columns": mapped_columns,
        "hidden_columns": hidden_columns,
        "filters": filter_list,
    }


def _is_safe_identifier(value: str) -> bool:
    return bool(value) and value.replace("_", "").replace("$", "").isalnum()


def _split_dataset_name(dataset: str):
    if "." in dataset:
        return dataset.split(".", 1)
    return None, dataset


def _qualify_dataset_name(schema_name: str, table_name: str) -> str:
    return table_name if schema_name == "public" else f"{schema_name}.{table_name}"


def _get_schema_tables(db: Session):
    inspector = inspect(db.bind)
    schema_tables = []

    for schema_name in inspector.get_schema_names():
        if schema_name in SYSTEM_SCHEMAS or schema_name.startswith("pg_"):
            continue

        try:
            table_names = inspector.get_table_names(schema=schema_name)
        except Exception as exc:
            logger.warning(f"[datasets] Could not read tables for schema {schema_name}: {exc}")
            continue

        for table_name in table_names:
            schema_tables.append((schema_name, table_name))

    schema_tables.sort(key=lambda item: (PREFERRED_SCHEMA_ORDER.get(item[0], 99), item[0], item[1]))
    return schema_tables


def _resolve_dataset(db: Session, dataset: str):
    inspector = inspect(db.bind)
    schema_name, table_name = _split_dataset_name(dataset)

    if schema_name:
        if schema_name in SYSTEM_SCHEMAS:
            return None
        try:
            tables = inspector.get_table_names(schema=schema_name)
        except Exception:
            return None
        if table_name in tables:
            return schema_name, table_name
        return None

    for candidate_schema in sorted(inspector.get_schema_names(), key=lambda s: PREFERRED_SCHEMA_ORDER.get(s, 99)):
        if candidate_schema in SYSTEM_SCHEMAS or candidate_schema.startswith("pg_"):
            continue
        try:
            tables = inspector.get_table_names(schema=candidate_schema)
        except Exception:
            continue
        if table_name in tables:
            return candidate_schema, table_name
    return None


def _get_table_object(db: Session, schema_name: str, table_name: str):
    metadata = MetaData()
    return Table(table_name, metadata, autoload_with=db.bind, schema=schema_name if schema_name != "public" else None)


def _estimate_row_count(db: Session, schema_name: str, table_name: str) -> int:
    """Get a fast row estimate from PostgreSQL statistics instead of COUNT(*)."""
    try:
        logger.info(
            "[datasets/hierarchical] SQL executed: SELECT COALESCE(c.reltuples::bigint, 0) "
            "FROM pg_class c JOIN pg_namespace n ON n.oid = c.relnamespace "
            "WHERE n.nspname = :schema_name AND c.relname = :table_name AND c.relkind IN ('r', 'p')"
        )
        result = db.execute(
            text(
                """
                SELECT COALESCE(c.reltuples::bigint, 0)
                FROM pg_class c
                JOIN pg_namespace n ON n.oid = c.relnamespace
                WHERE n.nspname = :schema_name
                  AND c.relname = :table_name
                  AND c.relkind IN ('r', 'p')
                """
            ),
            {"schema_name": schema_name, "table_name": table_name},
        ).scalar()
        return max(0, int(result or 0))
    except Exception as error:
        logger.debug(f"[row-estimate] Falling back to 0 for {schema_name}.{table_name}: {error}")
        return 0


def _get_columns_for_dataset(db: Session, dataset: str):
    resolved = _resolve_dataset(db, dataset)
    if not resolved:
        return []

    schema_name, table_name = resolved
    inspector = inspect(db.bind)
    columns = inspector.get_columns(table_name, schema=schema_name)
    return [
        {
            'name': col['name'],
            'type': str(col['type']),
        }
        for col in columns
    ]


# ═══════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════

def get_table_columns(db: Session, table_name: str) -> List[Dict[str, str]]:
    """Get all columns from a table with their types"""
    try:
        resolved = _resolve_dataset(db, table_name)
        if not resolved:
            return []

        schema_name, resolved_table = resolved
        inspector = inspect(db.bind)
        columns = inspector.get_columns(resolved_table, schema=schema_name)
        return [
            {
                'name': col['name'],
                'type': str(col['type']),
            }
            for col in columns
        ]
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
        resolved = _resolve_dataset(db, table_name)
        if not resolved:
            logger.error(f"Table {table_name} not found")
            return []
        schema_name, resolved_table = resolved
        
        # Build query with applied filters
        metadata = MetaData()
        table = Table(resolved_table, metadata, autoload_with=db.bind, schema=schema_name if schema_name != 'public' else None)
        
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


def get_ec_distinct_options(
    db: Session,
    column_name: str,
    limit: int = 1000,
    offset: int = 0,
    applied_filters: Optional[Dict] = None,
) -> List[Dict[str, Any]]:
    applied_filters = applied_filters or {}
    params = {"limit": limit, "offset": offset}

    if column_name == "state_code":
        rows = db.execute(
            text(
                """
                SELECT sc.state_code AS value, sc.state_name AS label
                FROM economic_census.state_codes sc
                WHERE EXISTS (
                    SELECT 1
                    FROM economic_census.enterprises_full e
                    WHERE NULLIF(e.state_code, '')::integer = sc.state_code
                )
                ORDER BY sc.state_name
                LIMIT :limit OFFSET :offset
                """
            ),
            params,
        ).fetchall()
    elif column_name == "district_code":
        state_filter = applied_filters.get("state_code")
        where_state = ""
        if state_filter not in (None, ""):
            where_state = "AND dc.state_code = :state_code"
            params["state_code"] = int(state_filter)
        rows = db.execute(
            text(
                f"""
                SELECT dc.district_code AS value,
                       dc.district_name AS label,
                       dc.state_code AS parent_value
                FROM economic_census.district_codes dc
                WHERE EXISTS (
                    SELECT 1
                    FROM economic_census.enterprises_full e
                    WHERE NULLIF(e.state_code, '')::integer = dc.state_code
                      AND NULLIF(e.district_code, '')::integer = dc.district_code
                )
                {where_state}
                ORDER BY dc.district_name
                LIMIT :limit OFFSET :offset
                """
            ),
            params,
        ).fetchall()
    elif column_name == "activity_code":
        category_filter = applied_filters.get("major_activity_code")
        where_category = ""
        if category_filter not in (None, ""):
            where_category = "AND e.major_activity_code = :major_activity_code"
            params["major_activity_code"] = str(category_filter)
        rows = db.execute(
            text(
                f"""
                SELECT e.activity_code AS value,
                       COALESCE(n.description, 'Unmapped activity code') AS label
                FROM economic_census.enterprises_full e
                LEFT JOIN economic_census.nic_codes n ON e.activity_code = n.nic_code
                WHERE e.activity_code IS NOT NULL
                  AND btrim(e.activity_code) <> ''
                  {where_category}
                GROUP BY e.activity_code, n.description
                ORDER BY e.activity_code
                LIMIT :limit OFFSET :offset
                """
            ),
            params,
        ).fetchall()
    elif column_name == "major_activity_code":
        rows = db.execute(
            text(
                """
                SELECT major_activity_code AS value,
                       'Activity category ' || btrim(major_activity_code) AS label
                FROM economic_census.enterprises_full
                WHERE major_activity_code IS NOT NULL
                  AND btrim(major_activity_code) <> ''
                GROUP BY major_activity_code
                ORDER BY major_activity_code
                LIMIT :limit OFFSET :offset
                """
            ),
            params,
        ).fetchall()
    else:
        resolved = _resolve_dataset(db, EC_ENTERPRISES_DATASET)
        if not resolved:
            return []
        schema_name, resolved_table = resolved
        table = _get_table_object(db, schema_name, resolved_table)
        if not hasattr(table.c, column_name):
            return []
        query = db.query(distinct(getattr(table.c, column_name)))
        for filter_col, filter_val in applied_filters.items():
            if filter_col != column_name and hasattr(table.c, filter_col) and filter_val not in (None, ""):
                query = query.filter(getattr(table.c, filter_col) == str(filter_val))
        raw_values = [row[0] for row in query.order_by(getattr(table.c, column_name)).limit(limit).offset(offset).all() if row[0] not in (None, "")]
        return [{"value": value, "label": str(value)} for value in raw_values]

    return [
        {
            "value": row[0],
            "label": f"{row[0]} - {row[1]}" if row[1] else str(row[0]),
            **({"parent_value": row[2]} if len(row) > 2 else {}),
        }
        for row in rows
    ]


def build_filter_conditions(db: Session, table_name: str, filters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build WHERE conditions from filter dictionary
    Handles different data types automatically
    """
    try:
        metadata = MetaData()
        resolved = _resolve_dataset(db, table_name)
        if not resolved:
            return {}
        schema_name, resolved_table = resolved
        table = Table(resolved_table, metadata, autoload_with=db.bind, schema=schema_name if schema_name != 'public' else None)
        
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

def _categorize_dataset_table(table: str) -> str:
    """Map a table name to a frontend-friendly hierarchical category."""
    table_lower = table.lower()
    if table_lower.startswith("economic_census.") or "enterprise" in table_lower or table_lower in {"state_codes", "district_codes", "nic_codes", "variable_metadata", "survey_metadata"}:
        return "Economic Census"
    if table_lower.startswith("plfs.") or table_lower.startswith("plfs_") or "plfs" in table_lower:
        return "PLFS"
    if table_lower.startswith("hces_") or "hces" in table_lower:
        return "HCES"
    if table_lower in ("person_survey", "household_survey", "survey_data", "census_data"):
        return "Survey"
    return "Other"


def _json_dataset_response(success: bool, data: Optional[Dict] = None, datasets: Optional[List[Dict[str, Any]]] = None,
                           error: Optional[str] = None, total_datasets: int = 0, status_code: int = 200) -> JSONResponse:
    """Always return valid JSON with a consistent envelope."""
    payload = {
        "success": success,
        "data": data if data is not None else {},
        "datasets": datasets if datasets is not None else [],
        "total_datasets": total_datasets,
    }
    if error:
        payload["error"] = error
    return JSONResponse(status_code=status_code, content=payload)


@router.get("/datasets/hierarchical")
async def get_hierarchical_datasets():
    """
    Get all available datasets organized hierarchically.
    Always returns valid JSON (HTTP 200) even when the database is unavailable.
    """
    t_start = time.time()
    logger.info("[datasets/hierarchical] Request received")

    if SessionLocal is None:
        logger.error("[datasets/hierarchical] Database session factory not initialized")
        return JSONResponse(
            status_code=200,
            content={
                "success": False,
                "error": "Database engine not initialized. Check database configuration.",
                "data": {},
                "categories": [],
                "datasets": [],
                "counts": {"total": 0},
                "total_datasets": 0
            }
        )

    db = SessionLocal()
    try:
        # Step 1: Query public.datasets table for user metadata if it exists
        db_datasets = {}
        try:
            cur = db.execute(text("SELECT name, table_name, description, config FROM public.datasets"))
            for row in cur.fetchall():
                db_datasets[row[1]] = {
                    "display_name": row[0],
                    "description": row[2],
                    "config": row[3] or {}
                }
        except Exception as e:
            logger.warning(f"[datasets/hierarchical] Could not query public.datasets table: {e}")

        # Step 2: Query DB catalog to fetch all schemas, tables, row counts, and column counts in one single query
        t_sql_start = time.time()
        catalog_query = text("""
            SELECT 
                n.nspname AS schema_name,
                c.relname AS table_name,
                COALESCE(c.reltuples::bigint, 0) AS row_count,
                (
                    SELECT count(*) 
                    FROM pg_attribute a 
                    WHERE a.attrelid = c.oid AND a.attnum > 0 AND NOT a.attisdropped
                ) AS column_count
            FROM pg_class c
            JOIN pg_namespace n ON n.oid = c.relnamespace
            WHERE n.nspname NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
              AND n.nspname NOT LIKE 'pg_temp_%'
              AND c.relkind IN ('r', 'p', 'v', 'm')
            ORDER BY 
                CASE n.nspname
                    WHEN 'public' THEN 0
                    WHEN 'economic_census' THEN 1
                    WHEN 'plfs' THEN 2
                    ELSE 3
                END,
                n.nspname,
                c.relname
        """)
        result = db.execute(catalog_query).fetchall()
        sql_time = time.time() - t_sql_start
        logger.info(f"[datasets/hierarchical] SQL execution time: {sql_time:.4f}s. Rows returned: {len(result)}")

        # Step 3: Categorize and assemble the response payload
        hierarchical = {}
        flat_datasets = []
        counts = {"total": 0}

        for row in result:
            schema_name = row[0]
            table_name = row[1]
            row_estimate = max(0, int(row[2]))
            col_count = int(row[3])

            # Filter/Skip system tables in public schema
            if schema_name == "public" and table_name in {
                "users", "sessions", "otp_challenges", "transactions", "usage_logs", "datasets", "data_records"
            }:
                continue

            # Determine category
            category = "Other"
            qualified_name = table_name if schema_name == "public" else f"{schema_name}.{table_name}"
            t_lower = qualified_name.lower()

            if "hces" in t_lower:
                category = "HCES"
            elif "plfs" in t_lower or "person_survey" in t_lower or "household_survey" in t_lower:
                category = "PLFS"
            elif "economic_census" in t_lower or "enterprise" in t_lower:
                category = "Economic Census"
            elif schema_name == "public":
                category = "Public"

            # Enrich display name & description from public.datasets metadata
            db_info = db_datasets.get(table_name) or db_datasets.get(qualified_name) or {}
            display_name = db_info.get("display_name") or table_name.replace("_", " ").title()

            dataset_item = {
                "name": qualified_name,
                "schema": schema_name,
                "table": table_name,
                "display_name": display_name,
                "row_count": row_estimate,
                "column_count": col_count,
                "description": db_info.get("description", ""),
                "config": db_info.get("config", {})
            }

            hierarchical.setdefault(category, []).append(dataset_item)
            flat_datasets.append(dataset_item)
            counts[category] = counts.get(category, 0) + 1
            counts["total"] += 1

        logger.info(
            f"[datasets/hierarchical] Response sent. Total time: {time.time() - t_start:.4f}s. "
            f"Returned {counts['total']} datasets across {len(hierarchical)} categories."
        )

        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "data": hierarchical,
                "categories": list(hierarchical.keys()),
                "datasets": flat_datasets,
                "counts": counts,
                "total_datasets": counts["total"]
            }
        )

    except Exception as e:
        logger.error(f"[datasets/hierarchical] Error: {e}", exc_info=True)
        return JSONResponse(
            status_code=200,
            content={
                "success": False,
                "error": f"Error fetching hierarchical datasets: {str(e)}",
                "data": {},
                "categories": [],
                "datasets": [],
                "counts": {"total": 0},
                "total_datasets": 0
            }
        )
    finally:
        db.close()


@router.get("/columns/{dataset}")
async def get_dataset_columns(
    dataset: str,
    db: Session = Depends(get_db)
):
    """
    Get all columns for a dataset
    """
    try:
        logger.info(f"[columns] dataset requested: {dataset}")
        columns = get_table_columns(db, dataset)
        if not columns:
            return {
                'success': False,
                'error': f"Dataset '{dataset}' not found",
                'columns': []
            }

        ux_profile = _ec_ux_profile(db, columns) if _is_ec_enterprises(dataset) else None
        response_columns = ux_profile["columns"] if ux_profile else columns
        
        logger.info(f"Retrieved {len(columns)} columns for dataset {dataset}")
        return {
            'success': True,
            'columns': response_columns,
            'total': len(columns),
            'ux_profile': ux_profile,
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
        logger.info(f"[distinct] dataset={dataset}, column={column}, limit={limit}, offset={offset}, filters={filters}")
        # Parse applied filters if provided
        applied_filters = {}
        if filters:
            try:
                applied_filters = json.loads(filters)
            except:
                pass
        
        if _is_ec_enterprises(dataset):
            values = get_ec_distinct_options(db, column, limit, offset, applied_filters)
        else:
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


@router.get("/ux-report/{dataset}")
async def get_dataset_ux_report(dataset: str, db: Session = Depends(get_db)):
    if not _is_ec_enterprises(dataset):
        return {
            "success": True,
            "dataset": dataset,
            "mapped_columns": [],
            "hidden_columns": [],
            "unmapped_codes": {},
            "filters": [],
        }

    try:
        columns = get_table_columns(db, dataset)
        profile = _ec_ux_profile(db, columns)
        unmapped = {}
        checks = {
            "state_code": """
                SELECT e.state_code, COUNT(*)
                FROM economic_census.enterprises_full e
                LEFT JOIN economic_census.state_codes s
                  ON NULLIF(e.state_code, '')::integer = s.state_code
                WHERE s.state_code IS NULL
                GROUP BY e.state_code
                ORDER BY COUNT(*) DESC
                LIMIT 50
            """,
            "district_code": """
                SELECT e.state_code || ':' || e.district_code, COUNT(*)
                FROM economic_census.enterprises_full e
                LEFT JOIN economic_census.district_codes d
                  ON NULLIF(e.state_code, '')::integer = d.state_code
                 AND NULLIF(e.district_code, '')::integer = d.district_code
                WHERE d.district_code IS NULL
                GROUP BY e.state_code, e.district_code
                ORDER BY COUNT(*) DESC
                LIMIT 50
            """,
            "activity_code": """
                SELECT e.activity_code, COUNT(*)
                FROM economic_census.enterprises_full e
                LEFT JOIN economic_census.nic_codes n ON e.activity_code = n.nic_code
                WHERE n.nic_code IS NULL
                GROUP BY e.activity_code
                ORDER BY COUNT(*) DESC
                LIMIT 50
            """,
        }
        for column_name, sql in checks.items():
            rows = db.execute(text(sql)).fetchall()
            unmapped[column_name] = [
                {"code": row[0], "rows": int(row[1])}
                for row in rows
            ]

        return {
            "success": True,
            "dataset": dataset,
            "mapped_columns": profile["mapped_columns"],
            "hidden_columns": profile["hidden_columns"],
            "unmapped_codes": unmapped,
            "filters": profile["filters"],
        }
    except Exception as e:
        logger.error(f"Error building UX report for {dataset}: {e}", exc_info=True)
        return {
            "success": False,
            "dataset": dataset,
            "error": str(e),
            "mapped_columns": [],
            "hidden_columns": [],
            "unmapped_codes": {},
            "filters": [],
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
        
        resolved = _resolve_dataset(db, table)
        if not resolved:
            return {
                'success': False,
                'error': f"Table '{table}' not found",
                'data': [],
                'total': 0
            }
        schema_name, table_name = resolved
        
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
        db_table = Table(table_name, metadata, autoload_with=db.bind, schema=schema_name if schema_name != 'public' else None)
        
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
        states = []
        inspector = inspect(db.bind)

        for schema_name, table_name in _get_schema_tables(db):
            try:
                columns = inspector.get_columns(table_name, schema=schema_name)
                for col_name in ['state_code', 'State_Code', 'State_UT_Code']:
                    if any(col['name'] == col_name for col in columns):
                        db_table = _get_table_object(db, schema_name, table_name)
                        state_query = db.query(distinct(getattr(db_table.c, col_name))).order_by(getattr(db_table.c, col_name))
                        for (state_code,) in state_query.limit(37).all():
                            if state_code is not None:
                                states.append({
                                    'state_code': state_code,
                                    'state_name': f'State {state_code}',
                                    'source_table': _qualify_dataset_name(schema_name, table_name),
                                })
                        break

                if states:
                    break
            except Exception as table_error:
                logger.debug(f"[reference/states] Skipping {schema_name}.{table_name}: {table_error}")
        
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
        for schema_name, table_name in _get_schema_tables(db):
            try:
                columns = inspector.get_columns(table_name, schema=schema_name)
                for col_name in ['district_code', 'District_Code']:
                    if any(col['name'] == col_name for col in columns):
                        db_table = _get_table_object(db, schema_name, table_name)
                        query = db.query(distinct(getattr(db_table.c, col_name)))

                        if state_code:
                            for state_col_name in ['state_code', 'State_Code', 'State_UT_Code']:
                                if any(col['name'] == state_col_name for col in columns):
                                    query = query.filter(getattr(db_table.c, state_col_name) == state_code)
                                    break

                        district_query = query.order_by(getattr(db_table.c, col_name))
                        for (district_code,) in district_query.limit(1000).all():
                            if district_code is not None:
                                districts.append({
                                    'district_code': district_code,
                                    'district_name': f'District {district_code}',
                                    'state_code': state_code,
                                    'source_table': _qualify_dataset_name(schema_name, table_name),
                                })
                        break

                if districts:
                    break
            except Exception as table_error:
                logger.debug(f"[reference/districts] Skipping {schema_name}.{table_name}: {table_error}")
        
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

        for schema_name, table_name in _get_schema_tables(db):
            if schema_name != 'economic_census':
                continue
            try:
                columns = inspector.get_columns(table_name, schema=schema_name)
                for col_name in ['state_code', 'State_Code', 'State_UT_Code']:
                    if any(col['name'] == col_name for col in columns):
                        db_table = _get_table_object(db, schema_name, table_name)
                        state_query = db.query(distinct(getattr(db_table.c, col_name))).order_by(getattr(db_table.c, col_name))
                        for (state_code,) in state_query.limit(37).all():
                            if state_code is not None:
                                states.append({
                                    'state_code': state_code,
                                    'state_name': f'State {state_code}',
                                    'source_table': _qualify_dataset_name(schema_name, table_name),
                                })
                        break

                if states:
                    break
            except Exception as table_error:
                logger.debug(f"[reference/ec/states] Skipping {schema_name}.{table_name}: {table_error}")

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

        for schema_name, table_name in _get_schema_tables(db):
            if schema_name != 'economic_census':
                continue
            try:
                columns = inspector.get_columns(table_name, schema=schema_name)
                for col_name in ['district_code', 'District_Code']:
                    if any(col['name'] == col_name for col in columns):
                        db_table = _get_table_object(db, schema_name, table_name)

                        query = db.query(distinct(getattr(db_table.c, col_name)))

                        if state_code:
                            for state_col_name in ['state_code', 'State_Code', 'State_UT_Code']:
                                if any(col['name'] == state_col_name for col in columns):
                                    query = query.filter(getattr(db_table.c, state_col_name) == state_code)
                                    break

                        district_query = query.order_by(getattr(db_table.c, col_name))
                        for (district_code,) in district_query.limit(1000).all():
                            if district_code is not None:
                                districts.append({
                                    'district_code': district_code,
                                    'district_name': f'District {district_code}',
                                    'state_code': state_code,
                                    'source_table': _qualify_dataset_name(schema_name, table_name),
                                })
                        break

                if districts:
                    break
            except Exception as table_error:
                logger.debug(f"[reference/ec/districts] Skipping {schema_name}.{table_name}: {table_error}")

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


@router.get("/analytics/summary")
async def get_analytics_summary(db: Session = Depends(get_db)):
    """Get summary statistics across all discovered datasets."""
    try:
        inspector = inspect(db.bind)
        summary = []

        for schema_name, table_name in _get_schema_tables(db):
            try:
                row_count = _estimate_row_count(db, schema_name, table_name)
                columns = inspector.get_columns(table_name, schema=schema_name)
                summary.append({
                    'table': _qualify_dataset_name(schema_name, table_name),
                    'schema': schema_name,
                    'rows': row_count,
                    'columns': len(columns),
                    'numeric_columns': sum(
                        1
                        for col in columns
                        if 'int' in str(col.get('type', '')).lower()
                        or 'numeric' in str(col.get('type', '')).lower()
                        or 'decimal' in str(col.get('type', '')).lower()
                        or 'real' in str(col.get('type', '')).lower()
                        or 'double precision' in str(col.get('type', '')).lower()
                    ),
                })
            except Exception as table_error:
                logger.debug(f"[analytics/summary] Skipping {schema_name}.{table_name}: {table_error}")

        total_rows = sum(item['rows'] for item in summary)
        logger.info(f"[analytics/summary] tables={len(summary)} total_rows={total_rows}")

        return {
            'success': True,
            'summary': summary,
            'total_tables': len(summary),
            'total_rows': total_rows,
        }
    except Exception as e:
        logger.error(f"Error fetching analytics summary: {e}")
        return {
            'success': False,
            'error': str(e),
            'summary': [],
            'total_tables': 0,
            'total_rows': 0,
        }



async def get_dataset_statistics(
    dataset: str,
    filters: Optional[str] = QueryParam(None),
    db: Session = Depends(get_db)
):
    """Get basic statistics for a dataset"""
    try:
        resolved = _resolve_dataset(db, dataset)
        if not resolved:
            return {
                'success': False,
                'error': f"Dataset '{dataset}' not found",
                'statistics': {}
            }
        schema_name, table_name = resolved
        
        # Parse filters
        applied_filters = {}
        if filters:
            try:
                applied_filters = json.loads(filters)
            except:
                pass
        
        # Get total count
        db_table = _get_table_object(db, schema_name, table_name)
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
                'dataset_name': _qualify_dataset_name(schema_name, table_name)
            }
        }
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        return {
            'success': False,
            'error': str(e),
            'statistics': {}
        }
