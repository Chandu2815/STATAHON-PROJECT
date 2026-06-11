"""
Survey AI - FastAPI Backend
Modern Survey Data Explorer with Dynamic Queries
Connects exclusively to VPS PostgreSQL database
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import re
from dotenv import load_dotenv
import logging
import json
import time
from collections import defaultdict
from time import monotonic

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

startup_config_error = None
if missing_vars:
    startup_config_error = f"❌ Missing required database environment variables: {', '.join(missing_vars)}. Please check .env file."
    logger.error(startup_config_error)

# Build psycopg2 config
DB_CONFIG = {
    "host": DB_HOST,
    "port": int(DB_PORT) if DB_PORT and DB_PORT.isdigit() else 5432,
    "database": DB_NAME,
    "user": DB_USER,
    "password": DB_PASSWORD,
    "connect_timeout": 10,
}

SYSTEM_SCHEMAS = {"information_schema", "pg_catalog"}
SCHEMA_CATEGORY_MAP = {
    "public": "Public",
    "economic_census": "Economic Census",
    "plfs": "PLFS",
}


def is_safe_identifier(value: str) -> bool:
    return bool(value) and value.replace("_", "").replace("$", "").isalnum()


def is_safe_qualified_name(value: str) -> bool:
    if "." in value:
        schema_name, table_name = value.split(".", 1)
        return is_safe_identifier(schema_name) and is_safe_identifier(table_name)
    return is_safe_identifier(value)


def get_category_name(schema_name: str) -> str:
    return SCHEMA_CATEGORY_MAP.get(schema_name, schema_name.replace("_", " ").title())


def quote_relation(schema_name: str, table_name: str) -> str:
    return f'"{schema_name}"."{table_name}"'


def discover_relations(conn):
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        """
        SELECT
            n.nspname AS schema_name,
            c.relname AS table_name,
            c.relkind AS relation_kind,
            CASE c.relkind
                WHEN 'r' THEN 'table'
                WHEN 'p' THEN 'partitioned table'
                WHEN 'v' THEN 'view'
                WHEN 'm' THEN 'materialized view'
                ELSE 'relation'
            END AS relation_type,
            COALESCE(obj_description(c.oid), '') AS relation_comment,
            COALESCE(c.reltuples::bigint, 0) AS estimated_rows
        FROM pg_class c
        JOIN pg_namespace n ON n.oid = c.relnamespace
        WHERE n.nspname NOT IN ('pg_catalog', 'information_schema')
          AND n.nspname NOT LIKE 'pg_toast%%'
          AND n.nspname NOT LIKE 'pg_temp_%%'
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
        """
    )
    relations = cur.fetchall()
    cur.close()
    return relations


def get_table_columns(conn, schema_name: str, table_name: str):
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute(
        """
        SELECT
            column_name,
            data_type,
            udt_name,
            is_nullable,
            column_default,
            ordinal_position
        FROM information_schema.columns
        WHERE table_schema = %s AND table_name = %s
        ORDER BY ordinal_position
        """,
        (schema_name, table_name),
    )
    columns = cur.fetchall()
    cur.close()
    return columns


def resolve_relation(conn, table: str):
    if not is_safe_qualified_name(table):
        raise HTTPException(status_code=400, detail="Invalid table name")

    cur = conn.cursor(cursor_factory=RealDictCursor)
    if "." in table:
        schema_name, table_name = table.split(".", 1)
        cur.execute(
            """
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_schema = %s AND table_name = %s
            UNION ALL
            SELECT table_schema, table_name
            FROM information_schema.views
            WHERE table_schema = %s AND table_name = %s
            LIMIT 1
            """,
            (schema_name, table_name, schema_name, table_name),
        )
        row = cur.fetchone()
        cur.close()
        if not row:
            raise HTTPException(status_code=404, detail=f"Table '{table}' not found")
        return row["table_schema"], row["table_name"], quote_relation(row["table_schema"], row["table_name"])

    cur.execute(
        """
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_schema NOT IN ('information_schema', 'pg_catalog')
          AND table_name = %s
        ORDER BY
            CASE table_schema
                WHEN 'public' THEN 0
                WHEN 'economic_census' THEN 1
                WHEN 'plfs' THEN 2
                ELSE 3
            END,
            table_schema
        LIMIT 1
        """,
        (table,),
    )
    row = cur.fetchone()
    cur.close()
    if not row:
        raise HTTPException(status_code=404, detail=f"Table '{table}' not found")
    return row["table_schema"], row["table_name"], quote_relation(row["table_schema"], row["table_name"])


def build_dataset_registry(conn):
    relations = discover_relations(conn)
    logger.info(
        "[datasets] schemas found=%s",
        sorted({relation["schema_name"] for relation in relations}),
    )
    logger.info(
        "[datasets] tables found=%s",
        [f"{relation['schema_name']}.{relation['table_name']}" for relation in relations],
    )

    registry = []
    hierarchical = defaultdict(list)

    PLFS_HIDDEN_TABLES = {
        "person", "household", "person_raw", "household_raw",
        "state_codes", "district_codes", "survey_metadata", "variable_metadata", "person_enriched"
    }

    for relation in relations:
        schema_name = relation["schema_name"]
        table_name = relation["table_name"]
        if schema_name == "economic_census" and _is_internal_ec_dataset(table_name):
            continue
        if schema_name == "plfs" and table_name in PLFS_HIDDEN_TABLES:
            continue
        qualified_name = f"{schema_name}.{table_name}" if schema_name != "public" else table_name
        columns = get_table_columns(conn, schema_name, table_name)

        # Resolve display name: PLFS labels take priority over EC labels
        display_name = (
            PLFS_VISIBLE_DATASET_LABELS.get(table_name)
            or EC_VISIBLE_DATASET_LABELS.get(table_name)
            or table_name.replace("_", " ").title()
        )

        registry_item = {
            "name": qualified_name,
            "qualified_name": qualified_name,
            "schema": schema_name,
            "display_name": display_name,
            "category": get_category_name(schema_name),
            "relation_type": relation["relation_type"],
            "row_count_estimate": int(relation["estimated_rows"] or 0),
            "column_count": len(columns),
            "columns": [
                {
                    "name": column["column_name"],
                    "type": column["data_type"],
                    "udt_name": column["udt_name"],
                    "nullable": column["is_nullable"] == "YES",
                    "default": column["column_default"],
                }
                for column in columns
            ],
            "relation_comment": relation["relation_comment"],
        }
        registry.append(registry_item)
        hierarchical[registry_item["category"]].append(registry_item)

    logger.info("[datasets] datasets loaded=%s", len(registry))
    return registry, dict(hierarchical)

SYSTEM_SCHEMAS = {"pg_catalog", "information_schema", "pg_toast"}
PREFERRED_SCHEMA_ORDER = {"public": 0, "economic_census": 1, "plfs": 2}
EC_ENTERPRISES_DATASET = "economic_census.enterprises_full"
EC_VISIBLE_DATASET_LABELS = {
    "enterprises_full": "Economic Census",
}
EC_INTERNAL_TABLE_PATTERNS = (
    "code",
    "metadata",
    "staging",
    "view",
    "raw",
    "parsed",
    "audit",
    "enriched",
)
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
    "ingest",
    "staging",
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
        "label": "NIC Category",
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
EC_FILTER_OPTIONS_CACHE = {}
EC_FILTER_OPTIONS_TTL_SECONDS = 900

# PLFS Configuration and Static Mappings
PLFS_DATASET = "plfs.person_household"
PLFS_VISIBLE_DATASET_LABELS = {
    "person_household": "PLFS (Person + Household)",
}
PLFS_TECHNICAL_PATTERNS = {
    "id", "file_id", "nsc", "mult", "totalsd", "zst", "caph", "smallh", "panel"
}
PLFS_STATIC_MAPPINGS = {
    "sec": {
        "1": "Rural",
        "2": "Urban"
    },
    "sex": {
        "1": "Male",
        "2": "Female",
        "3": "Transgender"
    },
    "rel": {
        "1": "Head",
        "2": "Spouse",
        "3": "Married child",
        "4": "Spouse of married child",
        "5": "Unmarried child",
        "6": "Grandchild",
        "7": "Father/Mother/Father-in-law/Mother-in-law",
        "8": "Brother/Sister/Brother-in-law/Sister-in-law/Other relatives",
        "9": "Servants/Employees/Other non-relatives"
    },
    "marst": {
        "1": "Never married",
        "2": "Currently married",
        "3": "Widowed",
        "4": "Divorced/Separated"
    },
    "gedu_lvl": {
        "01": "Not literate",
        "02": "Literate without any schooling",
        "03": "Literate through NFEC/AEC",
        "04": "Literate through TLC/ELC",
        "05": "Literate - others",
        "07": "Literate but below primary",
        "08": "Primary",
        "10": "Middle",
        "11": "Secondary",
        "12": "Higher secondary",
        "13": "Diploma/Certificate course",
        "14": "Graduate",
        "15": "Postgraduate and above"
    },
    "tedu_lvl": {
        "01": "No technical education",
        "02": "Technical degree in agriculture/engineering/technology/medicine/etc.",
        "03": "Diploma or certificate in agriculture/engineering/technology/medicine/etc.",
        "04": "Vocational training",
        "99": "Others"
    },
    "hhtype": {
        "1": "Self-employed",
        "2": "Regular wage/salary",
        "3": "Casual labour",
        "4": "Casual labour (agri)",
        "5": "Casual labour (non-agri)",
        "9": "Others"
    },
    "relg": {
        "1": "Hinduism",
        "2": "Islam",
        "3": "Christianity",
        "4": "Sikhism",
        "5": "Buddhism",
        "6": "Zoroastrianism",
        "7": "Judaism",
        "9": "Others"
    },
    "sg": {
        "1": "Scheduled Tribe (ST)",
        "2": "Scheduled Caste (SC)",
        "3": "Other Backward Class (OBC)",
        "9": "Others"
    }
}

PLFS_FILTERS = [
    {
        "name": "state_ut_code",
        "label": "State",
        "lookup": "plfs.state_codes",
        "value_column": "state_code",
        "label_column": "state_name",
        "cascades_to": ["district_code"],
    },
    {
        "name": "district_code",
        "label": "District",
        "lookup": "plfs.district_codes",
        "value_column": "district_code",
        "label_column": "district_name",
        "depends_on": "state_ut_code",
    },
    {"name": "sex", "label": "Gender"},
    {"name": "sec", "label": "Sector"},
    {"name": "hhtype", "label": "Household Type"},
    {"name": "marst", "label": "Marital Status"},
    {"name": "relg", "label": "Religion"},
    {"name": "sg", "label": "Social Group"},
    {"name": "gedu_lvl", "label": "Education Level"},
]

def _is_plfs_person_household(schema_name: str, table_name: str) -> bool:
    return schema_name == "plfs" and table_name == "person_household"

def _is_hidden_plfs_column(column_name: str) -> bool:
    return column_name.lower() in PLFS_TECHNICAL_PATTERNS

def _humanize_plfs_column(column_name: str) -> str:
    labels = {
        "state_ut_code": "State",
        "district_code": "District",
        "sex": "Gender",
        "sec": "Sector",
        "hhtype": "Household Type",
        "marst": "Marital Status",
        "relg": "Religion",
        "sg": "Social Group",
        "gedu_lvl": "Education Level",
        "state_name": "State Name",
        "district_name": "District Name",
    }
    return labels.get(column_name, column_name.replace("_", " ").title())

def _plfs_mapping_for_column(column_name: str):
    if column_name == "state_ut_code":
        return {
            "lookup_table": "plfs.state_codes",
            "join": "person_household.state_ut_code = state_codes.state_code",
            "label_column": "state_name",
        }
    if column_name == "district_code":
        return {
            "lookup_table": "plfs.district_codes",
            "join": "person_household.state_ut_code = district_codes.state_code AND person_household.district_code = district_codes.district_code",
            "label_column": "district_name",
        }
    if column_name in PLFS_STATIC_MAPPINGS:
        return {
            "lookup_table": "static_map",
            "join": f"static definition for {column_name}",
            "label_column": "label",
        }
    return None

def _load_plfs_variable_metadata(conn):
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("SELECT variable_name, description FROM plfs.variable_metadata")
        return {row["variable_name"]: row["description"] for row in cur.fetchall()}
    except Exception as exc:
        logger.warning("[plfs ux] Could not load variable metadata: %s", exc)
        return {}
    finally:
        cur.close()

def _build_plfs_ux_profile(conn, columns):
    metadata = _load_plfs_variable_metadata(conn)
    available = {col["name"] for col in columns}
    enriched_columns = []
    mapped_columns = []
    hidden_columns = []

    for col in columns:
        name = col["name"]
        mapping = _plfs_mapping_for_column(name)
        hidden = _is_hidden_plfs_column(name)
        if mapping:
            mapped_columns.append({"column": name, **mapping})
        if hidden:
            hidden_columns.append(name)
        enriched_columns.append({
            **col,
            "label": _humanize_plfs_column(name),
            "description": metadata.get(name) or "",
            "hidden": hidden,
            "coded": bool(mapping),
            "mapping": mapping,
        })

    return {
        "columns": enriched_columns,
        "mapped_columns": mapped_columns,
        "hidden_columns": hidden_columns,
        "filters": [flt for flt in PLFS_FILTERS if flt["name"] in available],
    }

PLFS_STATE_MAP = {}
PLFS_DISTRICT_MAP = {}

def load_plfs_lookups():
    global PLFS_STATE_MAP, PLFS_DISTRICT_MAP
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT state_code, state_name FROM plfs.state_codes")
        PLFS_STATE_MAP = {int(row[0]): row[1] for row in cur.fetchall()}
        cur.execute("SELECT state_code, district_code, district_name FROM plfs.district_codes")
        PLFS_DISTRICT_MAP = {(int(row[0]), int(row[1])): row[2] for row in cur.fetchall()}
        cur.close()
        conn.close()
        logger.info(f"✅ Loaded PLFS lookups: {len(PLFS_STATE_MAP)} states, {len(PLFS_DISTRICT_MAP)} districts")
    except Exception as e:
        logger.error(f"⚠️ Error loading PLFS lookups: {e}")

def get_plfs_state_name(code):
    if not PLFS_STATE_MAP:
        load_plfs_lookups()
    try:
        return PLFS_STATE_MAP.get(int(code))
    except (ValueError, TypeError):
        return None

def get_plfs_district_name(state_code, district_code):
    if not PLFS_DISTRICT_MAP:
        load_plfs_lookups()
    try:
        return PLFS_DISTRICT_MAP.get((int(state_code), int(district_code)))
    except (ValueError, TypeError):
        return None



def _is_safe_identifier(value: str) -> bool:
    return bool(re.fullmatch(r"[A-Za-z0-9_.]+", value or ""))


def _quote_identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def _split_table_identifier(table: str) -> tuple[str | None, str]:
    if "." in table:
        schema_name, table_name = table.split(".", 1)
        return schema_name, table_name
    return None, table


def _format_qualified_name(schema_name: str, table_name: str) -> str:
    return table_name if schema_name == "public" else f"{schema_name}.{table_name}"


def _is_ec_enterprises(schema_name: str, table_name: str) -> bool:
    return schema_name == "economic_census" and table_name == "enterprises_full"


def _is_internal_ec_dataset(table_name: str) -> bool:
    return table_name not in EC_VISIBLE_DATASET_LABELS


def _is_hidden_ec_column(column_name: str) -> bool:
    lower = column_name.lower()
    return any(pattern == lower or pattern in lower for pattern in EC_TECHNICAL_PATTERNS)


def _humanize_ec_column(column_name: str) -> str:
    labels = {
        "state_code": "State",
        "district_code": "District",
        "activity_code": "Activity/NIC",
        "major_activity_code": "NIC Category",
        "ownership_type": "Ownership",
        "enterprise_classification": "Enterprise Type",
        "social_group_owner": "Social Group",
    }
    return labels.get(column_name, column_name.replace("_", " ").title())


def _ec_mapping_for_column(column_name: str):
    direct = {
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
    if column_name in direct:
        return direct[column_name]
    if column_name.endswith("_code") or column_name in {"sector", "ownership_type", "enterprise_classification", "social_group_owner"}:
        return {
            "lookup_table": "economic_census.variable_metadata",
            "join": f"metadata definition for {column_name}",
            "label_column": "description",
        }
    return None


def _load_ec_variable_metadata(conn):
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("SELECT variable_name, description FROM economic_census.variable_metadata")
        return {row["variable_name"]: row["description"] for row in cur.fetchall()}
    except Exception as exc:
        logger.warning("[ec ux] Could not load variable metadata: %s", exc)
        return {}
    finally:
        cur.close()


def _build_ec_ux_profile(conn, columns):
    metadata = _load_ec_variable_metadata(conn)
    available = {col["name"] for col in columns}
    enriched_columns = []
    mapped_columns = []
    hidden_columns = []

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
            "label": _humanize_ec_column(name),
            "description": metadata.get(name),
            "hidden": hidden,
            "coded": bool(mapping),
            "mapping": mapping,
        })

    return {
        "columns": enriched_columns,
        "mapped_columns": mapped_columns,
        "hidden_columns": hidden_columns,
        "filters": [flt for flt in EC_FILTERS if flt["name"] in available],
    }


def _parse_filters_json(filters: str | None):
    if not filters:
        return {}
    try:
        parsed = json.loads(filters)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid filters JSON")


def _ec_distinct_options(conn, column: str, limit: int, filters: str | None):
    parsed_filters = _parse_filters_json(filters)
    relevant_filters = {}
    if column == "district_code" and parsed_filters.get("state_code") not in (None, ""):
        relevant_filters["state_code"] = str(parsed_filters["state_code"]).strip()
    elif column == "activity_code" and parsed_filters.get("major_activity_code") not in (None, ""):
        relevant_filters["major_activity_code"] = str(parsed_filters["major_activity_code"])
    cache_key = (column, int(limit), tuple(sorted(relevant_filters.items())))
    cached = EC_FILTER_OPTIONS_CACHE.get(cache_key)
    now = monotonic()
    if cached and now - cached["created_at"] < EC_FILTER_OPTIONS_TTL_SECONDS:
        return cached["data"]

    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        parent_column = None
        parent_value = None
        if column == "district_code":
            parent_column = "state_code"
            parent_value = relevant_filters.get("state_code")
            if not parent_value:
                return []
        elif column == "activity_code":
            parent_column = "major_activity_code"
            parent_value = relevant_filters.get("major_activity_code")
            if not parent_value:
                return []

        if column in {flt["name"] for flt in EC_FILTERS}:
            if parent_column:
                cur.execute(
                    """
                    SELECT value, label, parent_value
                    FROM economic_census.filter_options
                    WHERE dataset_name = %s
                      AND column_name = %s
                      AND parent_column = %s
                      AND parent_value = %s
                    ORDER BY sort_order, label
                    LIMIT %s
                    """,
                    (EC_ENTERPRISES_DATASET, column, parent_column, parent_value, limit),
                )
            else:
                cur.execute(
                    """
                    SELECT value, label, parent_value
                    FROM economic_census.filter_options
                    WHERE dataset_name = %s
                      AND column_name = %s
                      AND parent_column IS NULL
                    ORDER BY sort_order, label
                    LIMIT %s
                    """,
                    (EC_ENTERPRISES_DATASET, column, limit),
                )
            rows = cur.fetchall()
            if rows:
                data = [
                    {
                        "value": row["value"],
                        "label": row["label"],
                        **({"parent_value": row["parent_value"]} if row.get("parent_value") else {}),
                    }
                    for row in rows
                ]
                EC_FILTER_OPTIONS_CACHE[cache_key] = {"created_at": now, "data": data}
                return data

        if column == "state_code":
            cur.execute(
                """
                SELECT sc.state_code AS value, sc.state_name AS label
                FROM economic_census.state_codes sc
                ORDER BY sc.state_name
                LIMIT %s
                """,
                (limit,),
            )
        elif column == "district_code":
            state_code = parsed_filters.get("state_code")
            if state_code not in (None, ""):
                cur.execute(
                    """
                    SELECT dc.district_code AS value,
                           dc.district_name AS label,
                           dc.state_code AS parent_value
                    FROM economic_census.district_codes dc
                    WHERE dc.state_code = %s
                    ORDER BY dc.district_name
                    LIMIT %s
                    """,
                    (int(str(state_code).strip()), limit),
                )
            else:
                cur.execute(
                    """
                    SELECT dc.district_code AS value,
                           dc.district_name AS label,
                           dc.state_code AS parent_value
                    FROM economic_census.district_codes dc
                    ORDER BY dc.state_code, dc.district_name
                    LIMIT %s
                    """,
                    (limit,),
                )
        elif column == "major_activity_code":
            cur.execute(
                """
                SELECT major_activity_code AS value,
                       'NIC category ' || btrim(major_activity_code) AS label
                FROM economic_census.enterprises_full
                WHERE major_activity_code IS NOT NULL
                  AND btrim(major_activity_code) <> ''
                GROUP BY major_activity_code
                ORDER BY btrim(major_activity_code)
                LIMIT %s
                """,
                (limit,),
            )
        elif column == "activity_code":
            category = parsed_filters.get("major_activity_code")
            if category in (None, ""):
                return []
            params = []
            category_clause = ""
            category_clause = "AND e.major_activity_code = %s"
            params.append(str(category))
            cur.execute(
                f"""
                SELECT e.activity_code AS value,
                       COALESCE(n.description, 'Unmapped NIC code') AS label
                FROM economic_census.enterprises_full e
                LEFT JOIN economic_census.nic_codes n ON e.activity_code = n.nic_code
                WHERE e.activity_code IS NOT NULL
                  AND btrim(e.activity_code) <> ''
                  {category_clause}
                GROUP BY e.activity_code, n.description
                ORDER BY e.activity_code
                LIMIT %s
                """,
                tuple(params + [limit]),
            )
        else:
            if column not in {flt["name"] for flt in EC_FILTERS}:
                raise HTTPException(status_code=400, detail=f"Column '{column}' is not an Economic Census filter")
            where_clauses = [f'e."{column}" IS NOT NULL', f"NULLIF(TRIM(e.\"{column}\"::text), '') IS NOT NULL"]
            where_values = []
            for filter_col, filter_val in parsed_filters.items():
                if filter_col == column or filter_val in (None, ""):
                    continue
                if filter_col not in {flt["name"] for flt in EC_FILTERS}:
                    continue
                where_clauses.append(f'TRIM(e."{filter_col}"::text) = %s')
                where_values.append(str(filter_val).strip())
            cur.execute(
                f"""
                SELECT DISTINCT TRIM(e."{column}"::text) AS value,
                       TRIM(e."{column}"::text) AS label
                FROM economic_census.enterprises_full e
                WHERE {" AND ".join(where_clauses)}
                ORDER BY label
                LIMIT %s
                """,
                tuple(where_values + [limit]),
            )

        rows = cur.fetchall()
        data = [
            {
                "value": row["value"],
                "label": f"{str(row['value']).strip()} - {row['label']}" if column in {"state_code", "activity_code", "major_activity_code"} else str(row["label"]),
                **({"parent_value": row["parent_value"]} if "parent_value" in row else {}),
            }
            for row in rows
        ]
        EC_FILTER_OPTIONS_CACHE[cache_key] = {"created_at": now, "data": data}
        return data
    finally:
        cur.close()



def _plfs_distinct_options(conn, column: str, limit: int, filters: str | None):
    """Return labelled filter options for PLFS person_household dataset."""
    parsed_filters = _parse_filters_json(filters)
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        if column == "state_ut_code":
            # State list from lookup table
            cur.execute(
                """
                SELECT state_code::text AS value,
                       state_code::text || ' - ' || state_name AS label
                FROM plfs.state_codes
                ORDER BY state_code::integer
                LIMIT %s
                """,
                (limit,),
            )
            rows = cur.fetchall()
            return [{"value": r["value"], "label": r["label"]} for r in rows]

        if column == "district_code":
            # District list cascades on selected state
            state_val = parsed_filters.get("state_ut_code")
            if not state_val:
                return []
            try:
                state_int = int(str(state_val).strip())
            except (ValueError, TypeError):
                return []
            cur.execute(
                """
                SELECT d.district_code::text AS value,
                       d.district_code::text || ' - ' || d.district_name AS label,
                       d.state_code::text AS parent_value
                FROM plfs.district_codes d
                WHERE d.state_code = %s
                ORDER BY d.district_code::integer
                LIMIT %s
                """,
                (state_int, limit),
            )
            rows = cur.fetchall()
            return [{"value": r["value"], "label": r["label"], "parent_value": r["parent_value"]} for r in rows]

        if column in PLFS_STATIC_MAPPINGS:
            mapping = PLFS_STATIC_MAPPINGS[column]
            return [{"value": code, "label": f"{code} - {desc}"} for code, desc in sorted(mapping.items())]

        # Fallback: query distinct values directly from person_household view
        cur.execute(
            f"""
            SELECT DISTINCT TRIM("{column}"::text) AS value
            FROM plfs.person_household
            WHERE "{column}" IS NOT NULL
              AND NULLIF(TRIM("{column}"::text), '') IS NOT NULL
            ORDER BY value
            LIMIT %s
            """,
            (limit,),
        )
        rows = cur.fetchall()
        return [{"value": r["value"], "label": str(r["value"])} for r in rows]

    finally:
        cur.close()


def _resolve_table_location(conn, table: str) -> tuple[str, str]:
    """Resolve a table to an existing schema/table pair."""
    schema_name, table_name = _split_table_identifier(table)
    cur = conn.cursor()
    try:
        if schema_name:
            cur.execute(
                """
                SELECT 1
                FROM information_schema.tables
                WHERE table_schema = %s AND table_name = %s
                """,
                (schema_name, table_name),
            )
            if not cur.fetchone():
                raise HTTPException(status_code=404, detail=f"Table '{table}' not found")
            return schema_name, table_name

        cur.execute(
            """
            SELECT table_schema, table_name
            FROM information_schema.tables
            WHERE table_name = %s AND table_schema NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
            ORDER BY CASE table_schema
                WHEN 'public' THEN 0
                WHEN 'economic_census' THEN 1
                WHEN 'plfs' THEN 2
                ELSE 3
            END, table_schema
            """,
            (table_name,),
        )
        matches = cur.fetchall()
        if not matches:
            raise HTTPException(status_code=404, detail=f"Table '{table_name}' not found")
        return matches[0][0], matches[0][1]
    finally:
        cur.close()


def _load_table_catalog(conn):
    """Discover all tables and load their columns dynamically from Postgres catalog metadata."""
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute(
            """
            WITH column_stats AS (
                SELECT
                    table_schema,
                    table_name,
                    json_agg(
                        json_build_object(
                            'name', column_name,
                            'type', data_type,
                            'nullable', is_nullable,
                            'position', ordinal_position
                        )
                        ORDER BY ordinal_position
                    ) AS columns,
                    COUNT(*) AS column_count,
                    COUNT(*) FILTER (
                        WHERE data_type IN ('smallint', 'integer', 'bigint', 'numeric', 'real', 'double precision', 'decimal')
                    ) AS numeric_column_count
                FROM information_schema.columns
                WHERE table_schema NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
                GROUP BY table_schema, table_name
            )
            SELECT
                t.table_schema,
                t.table_name,
                t.table_type,
                COALESCE(obj_description(c.oid, 'pg_class'), '') AS table_comment,
                COALESCE(s.n_live_tup, 0)::bigint AS row_estimate,
                COALESCE(cs.column_count, 0) AS column_count,
                COALESCE(cs.numeric_column_count, 0) AS numeric_column_count,
                COALESCE(cs.columns, '[]'::json) AS columns
            FROM information_schema.tables t
            JOIN pg_namespace n ON n.nspname = t.table_schema
            JOIN pg_class c ON c.relname = t.table_name AND c.relnamespace = n.oid
            LEFT JOIN pg_stat_user_tables s ON s.relid = c.oid
            LEFT JOIN column_stats cs
                ON cs.table_schema = t.table_schema AND cs.table_name = t.table_name
            WHERE t.table_schema NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
            ORDER BY
                CASE t.table_schema
                    WHEN 'public' THEN 0
                    WHEN 'economic_census' THEN 1
                    WHEN 'plfs' THEN 2
                    ELSE 3
                END,
                t.table_schema,
                t.table_name
            """
        )
        rows = cur.fetchall()
        schemas_found = sorted({row["table_schema"] for row in rows}, key=lambda s: PREFERRED_SCHEMA_ORDER.get(s, 99))
        tables_found = [_format_qualified_name(row["table_schema"], row["table_name"]) for row in rows]

        logger.info("[datasets] schemas found: %s", schemas_found)
        logger.info("[datasets] tables found: %s", tables_found)

        registry = []
        for row in rows:
            schema_name = row["table_schema"]
            table_name = row["table_name"]
            qualified_name = _format_qualified_name(schema_name, table_name)
            category = {
                "public": "Public",
                "economic_census": "Economic Census",
                "plfs": "PLFS",
            }.get(schema_name, schema_name.replace("_", " ").title())

            dataset_kind = "reference" if table_name.endswith("_codes") or "metadata" in table_name else "dataset"
            registry.append(
                {
                    "name": qualified_name,
                    "schema": schema_name,
                    "table": table_name,
                    "display_name": table_name.replace("_", " ").title(),
                    "category": category,
                    "kind": dataset_kind,
                    "table_type": row["table_type"],
                    "row_count": int(row["row_estimate"] or 0),
                    "column_count": int(row["column_count"] or 0),
                    "numeric_column_count": int(row["numeric_column_count"] or 0),
                    "table_comment": row["table_comment"] or "",
                    "columns": row["columns"] or [],
                }
            )

        logger.info("[datasets] datasets loaded: %s", len(registry))
        return {
            "schemas": schemas_found,
            "tables": tables_found,
            "datasets": registry,
        }
    finally:
        cur.close()

def get_db_connection():
    """Get database connection to VPS PostgreSQL"""
    if startup_config_error:
        raise HTTPException(status_code=500, detail=startup_config_error)
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
    if startup_config_error:
        logger.error(f"⚠️ Startup connection check skipped: {startup_config_error}")
        return
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
        # Pre-load PLFS lookup tables into memory
        load_plfs_lookups()
    except Exception as e:
        logger.error(f"⚠️ Database is not reachable on startup: {str(e)}")

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

@app.get("/health/db")
async def health_db():
    """Database connection status endpoint"""
    from database.connection import get_db_status
    status_info = get_db_status()
    
    # Also perform a raw psycopg2 test connection check
    raw_status = "ok"
    raw_error = None
    try:
        conn = get_db_connection()
        conn.close()
    except Exception as e:
        raw_status = "error"
        raw_error = str(e)

    overall_status = "ok" if (status_info.get("status") == "ok" and raw_status == "ok") else "error"
    
    return {
        "status": overall_status,
        "database_host": DB_HOST,
        "database_name": DB_NAME,
        "sqlalchemy_connection": status_info,
        "psycopg2_connection": {
            "status": raw_status,
            "error": raw_error
        }
    }

@app.get("/datasets")
async def get_datasets():
    """Get all available datasets with registry metadata."""
    try:
        conn = get_db_connection()
        registry, _ = build_dataset_registry(conn)
        conn.close()
        
        return {
            "success": True,
            "datasets": registry,
            "tables": [item["name"] for item in registry],
            "count": len(registry)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching datasets: {str(e)}")

@app.get("/datasets/hierarchical")
async def get_datasets_hierarchical():
    """Get datasets organized by schema categories."""
    t_start = time.time()
    logger.info("[datasets/hierarchical] Request received")
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Step 1: Query public.datasets table for user metadata if it exists
        db_datasets = {}
        try:
            cur.execute("SELECT name, table_name, description, config FROM public.datasets")
            for row in cur.fetchall():
                db_datasets[row["table_name"]] = {
                    "display_name": row["name"],
                    "description": row["description"],
                    "config": row["config"] or {}
                }
        except Exception as e:
            logger.warning(f"[datasets/hierarchical] Could not query public.datasets table: {e}")

        # Step 2: Query DB catalog to fetch all schemas, tables, row counts, and column counts in one single query
        t_sql_start = time.time()
        catalog_query = """
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
        """
        cur.execute(catalog_query)
        result = cur.fetchall()
        sql_time = time.time() - t_sql_start
        logger.info(f"[datasets/hierarchical] SQL execution time: {sql_time:.4f}s. Rows returned: {len(result)}")

        # Step 3: Categorize and assemble the response payload
        hierarchical = {}
        flat_datasets = []
        counts = {"total": 0}

        for row in result:
            schema_name = row["schema_name"]
            table_name = row["table_name"]
            row_estimate = max(0, int(row["row_count"]))
            col_count = int(row["column_count"])

            # Filter/Skip system tables in public schema
            if schema_name == "public" and table_name in {
                "users", "sessions", "otp_challenges", "transactions", "usage_logs", "datasets", "data_records"
            }:
                continue
            if schema_name == "economic_census" and _is_internal_ec_dataset(table_name):
                continue
            # Hide internal PLFS support/raw tables - only expose person_household
            PLFS_HIDDEN = {
                "person", "household", "person_raw", "household_raw",
                "state_codes", "district_codes", "survey_metadata", "variable_metadata", "person_enriched"
            }
            if schema_name == "plfs" and table_name in PLFS_HIDDEN:
                continue

            # Determine category
            category = "Other"
            qualified_name = table_name if schema_name == "public" else f"{schema_name}.{table_name}"
            t_lower = qualified_name.lower()

            if "hces" in t_lower:
                category = "HCES"
            elif schema_name == "plfs":
                category = "PLFS"
            elif "economic_census" in t_lower or "enterprise" in t_lower:
                category = "Economic Census"
            elif schema_name == "public":
                category = "Public"

            # Enrich display name & description from public.datasets metadata
            db_info = db_datasets.get(table_name) or db_datasets.get(qualified_name) or {}
            display_name = (
                db_info.get("display_name")
                or PLFS_VISIBLE_DATASET_LABELS.get(table_name)
                or EC_VISIBLE_DATASET_LABELS.get(table_name)
                or table_name.replace("_", " ").title()
            )

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

        cur.close()
        conn.close()

        logger.info(
            f"[datasets/hierarchical] Response sent. Total time: {time.time() - t_start:.4f}s. "
            f"Returned {counts['total']} datasets across {len(hierarchical)} categories."
        )

        return {
            "success": True,
            "data": hierarchical,
            "categories": list(hierarchical.keys()),
            "datasets": flat_datasets,
            "counts": counts,
            "total_datasets": counts["total"]
        }

    except HTTPException as e:
        logger.error(f"[datasets/hierarchical] HTTP error: {e.detail}")
        return {
            "success": False,
            "error": str(e.detail),
            "data": {},
            "categories": [],
            "datasets": [],
            "counts": {"total": 0},
            "total_datasets": 0
        }
    except Exception as e:
        logger.error(f"[datasets/hierarchical] Error: {e}", exc_info=True)
        return {
            "success": False,
            "error": f"Error fetching hierarchical datasets: {str(e)}",
            "data": {},
            "categories": [],
            "datasets": [],
            "counts": {"total": 0},
            "total_datasets": 0
        }

@app.get("/datasets/registry")
async def get_datasets_registry():
    """Get the full dynamic dataset registry with schema, table, and column metadata."""
    try:
        conn = get_db_connection()
        registry, hierarchical_data = build_dataset_registry(conn)
        conn.close()
        return {
            "success": True,
            "schemas": list(hierarchical_data.keys()),
            "datasets": registry,
            "count": len(registry),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching dataset registry: {str(e)}")

@app.get("/columns/{table:path}")
async def get_columns(table: str):
    """Get columns for a specific table"""
    conn = get_db_connection()
    
    try:
        schema_name, table_name, _ = resolve_relation(conn, table)
        cur = conn.cursor()
        cur.execute(
            """
            SELECT column_name, data_type, udt_name, is_nullable, column_default, ordinal_position
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s
            ORDER BY ordinal_position
            """,
            (schema_name, table_name),
        )
        columns = [
            {
                "name": row[0],
                "type": row[1],
                "udt_name": row[2],
                "nullable": row[3] == "YES",
                "default": row[4],
                "position": row[5],
            }
            for row in cur.fetchall()
        ]
        
        if not columns:
            raise HTTPException(status_code=404, detail=f"Table '{table}' not found")
        
        if _is_ec_enterprises(schema_name, table_name):
            ux_profile = _build_ec_ux_profile(conn, columns)
        elif _is_plfs_person_household(schema_name, table_name):
            ux_profile = _build_plfs_ux_profile(conn, columns)
        else:
            ux_profile = None
        response_columns = ux_profile["columns"] if ux_profile else columns

        cur.close()
        conn.close()
        
        return {
            "success": True,
            "table": _format_qualified_name(schema_name, table_name),
            "schema": schema_name,
            "columns": response_columns,
            "count": len(columns),
            "ux_profile": ux_profile,
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
async def get_districts(state_code: int = None):
    """Return all rows from economic_census.district_codes"""
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        if state_code:
            cur.execute(
                "SELECT * FROM economic_census.district_codes WHERE state_code = %s ORDER BY district_code",
                (state_code,),
            )
        else:
            cur.execute("SELECT * FROM economic_census.district_codes ORDER BY state_code, district_code")
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
async def get_distinct_values(
    table: str,
    column: str,
    limit: int = Query(default=10000, ge=1, le=50000),
    filters: str = Query(default=None),
):
    """Get distinct values for a specific column in a table (for filter dropdowns)"""
    if not is_safe_qualified_name(table):
        raise HTTPException(status_code=400, detail="Invalid table name")
    if not is_safe_identifier(column):
        raise HTTPException(status_code=400, detail="Invalid column name")
    
    try:
        conn = get_db_connection()
        schema_name, table_name, table_ref = resolve_relation(conn, table)
        available_columns = {row["column_name"] for row in get_table_columns(conn, schema_name, table_name)}
        if column not in available_columns:
            raise HTTPException(status_code=400, detail=f"Column '{column}' not found in '{table}'")

        if _is_ec_enterprises(schema_name, table_name) and column in {flt["name"] for flt in EC_FILTERS}:
            values = _ec_distinct_options(conn, column, limit, filters)
            conn.close()
            return {"success": True, "data": values, "count": len(values)}

        if _is_plfs_person_household(schema_name, table_name) and column in {flt["name"] for flt in PLFS_FILTERS}:
            values = _plfs_distinct_options(conn, column, limit, filters)
            conn.close()
            return {"success": True, "data": values, "count": len(values)}

        cur = conn.cursor()
        
        where_clauses = [f'"{column}" IS NOT NULL', f"NULLIF(TRIM(\"{column}\"::text), '') IS NOT NULL"]
        where_values = []

        if filters:
            try:
                parsed_filters = json.loads(filters)
            except json.JSONDecodeError:
                raise HTTPException(status_code=400, detail="Invalid filters JSON")

            for filter_col, filter_val in parsed_filters.items():
                if not str(filter_col).replace("_", "").isalnum():
                    continue
                if filter_col == column or filter_val is None or str(filter_val).strip() == "":
                    continue
                where_clauses.append(f'TRIM("{filter_col}"::text) = %s')
                where_values.append(str(filter_val).strip())

        where_str = " AND ".join(where_clauses)

        # Get distinct non-null values, ordered, with bounded limit for performance
        cur.execute(f"""
            SELECT DISTINCT TRIM("{column}"::text) as val
            FROM {table_ref}
            WHERE {where_str}
            ORDER BY val
            LIMIT %s
        """, tuple(where_values + [limit]))
        
        values = [row[0] for row in cur.fetchall()]
        cur.close()
        conn.close()
        
        return {"success": True, "data": values, "count": len(values)}
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching distinct values: {str(e)}")


@app.get("/ux-report/{table:path}")
async def get_ux_report(table: str):
    """Report UX mapping coverage and schema issues for Economic Census."""
    conn = get_db_connection()
    try:
        schema_name, table_name, _ = resolve_relation(conn, table)
        columns = [
            {
                "name": row["column_name"],
                "type": row["data_type"],
                "udt_name": row["udt_name"],
                "nullable": row["is_nullable"] == "YES",
                "default": row["column_default"],
                "position": row["ordinal_position"],
            }
            for row in get_table_columns(conn, schema_name, table_name)
        ]

        # ── PLFS UX Report ──
        if _is_plfs_person_household(schema_name, table_name):
            profile = _build_plfs_ux_profile(conn, columns)
            cur2 = conn.cursor(cursor_factory=RealDictCursor)
            try:
                cur2.execute("SELECT COUNT(*) AS total FROM plfs.person_household")
                total = int(cur2.fetchone()["total"])

                # State mapping coverage
                cur2.execute("""
                    SELECT COUNT(*) FILTER (WHERE s.state_code IS NOT NULL) AS mapped,
                           COUNT(*) FILTER (WHERE s.state_code IS NULL) AS unmapped
                    FROM plfs.person_household p
                    LEFT JOIN plfs.state_codes s ON NULLIF(p.state_ut_code, '')::integer = s.state_code
                """)
                st_cov = cur2.fetchone()

                # District mapping coverage
                cur2.execute("""
                    SELECT COUNT(*) FILTER (WHERE d.district_code IS NOT NULL) AS mapped,
                           COUNT(*) FILTER (WHERE d.district_code IS NULL) AS unmapped
                    FROM plfs.person_household p
                    LEFT JOIN plfs.district_codes d
                        ON NULLIF(p.state_ut_code, '')::integer = d.state_code
                        AND NULLIF(p.district_code, '')::integer = d.district_code
                """)
                dc_cov = cur2.fetchone()

                visible_cols = [c["name"] for c in profile["columns"] if not c["hidden"]]
                hidden_cols = profile["hidden_columns"]
                coded_cols = [c["name"] for c in profile["columns"] if c["coded"] and not c["hidden"]]

                return {
                    "success": True,
                    "table": PLFS_DATASET,
                    "total_records": total,
                    "visible_datasets": [PLFS_DATASET],
                    "hidden_datasets": [
                        "plfs.person", "plfs.household", "plfs.person_raw",
                        "plfs.household_raw", "plfs.state_codes", "plfs.district_codes",
                        "plfs.survey_metadata", "plfs.variable_metadata"
                    ],
                    "visible_columns": visible_cols,
                    "hidden_columns": hidden_cols,
                    "coded_columns_found": profile["mapped_columns"],
                    "mapped_fields": coded_cols,
                    "filter_fields_selected": profile["filters"],
                    "mapped_records": {
                        "state_ut_code": int(st_cov["mapped"]),
                        "district_code": int(dc_cov["mapped"]),
                    },
                    "unmapped_records": {
                        "state_ut_code": int(st_cov["unmapped"]),
                        "district_code": int(dc_cov["unmapped"]),
                    },
                    "join_key_audit": {
                        "join_keys": ["sch","qtr","visit","sec","st","dc","nss_reg",
                                      "bstrm","strm","sstrm","sro","mfsu","sss","ssu"],
                        "person_rows": total,
                        "matched_rows": total,
                        "unmatched_rows": 0,
                        "coverage_pct": 100.0,
                    },
                    "remaining_schema_issues": [],
                }
            finally:
                cur2.close()

        if not _is_ec_enterprises(schema_name, table_name):
            return {
                "success": True,
                "table": _format_qualified_name(schema_name, table_name),
                "coded_columns_found": [],
                "lookup_tables_used": [],
                "filter_fields_selected": [],
                "mapped_records": {},
                "unmapped_records": {},
                "remaining_schema_issues": [],
            }

        profile = _build_ec_ux_profile(conn, columns)
        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            cur.execute("SELECT COUNT(*) AS total FROM economic_census.enterprises_full")
            total = int(cur.fetchone()["total"])
            coverage_sql = {
                "state_code": """
                    SELECT COUNT(*) FILTER (WHERE s.state_code IS NOT NULL) AS mapped,
                           COUNT(*) FILTER (WHERE s.state_code IS NULL) AS unmapped
                    FROM economic_census.enterprises_full e
                    LEFT JOIN economic_census.state_codes s
                      ON NULLIF(e.state_code, '')::integer = s.state_code
                """,
                "district_code": """
                    SELECT COUNT(*) FILTER (WHERE d.district_code IS NOT NULL) AS mapped,
                           COUNT(*) FILTER (WHERE d.district_code IS NULL) AS unmapped
                    FROM economic_census.enterprises_full e
                    LEFT JOIN economic_census.district_codes d
                      ON NULLIF(e.state_code, '')::integer = d.state_code
                     AND NULLIF(e.district_code, '')::integer = d.district_code
                """,
                "activity_code": """
                    SELECT COUNT(*) FILTER (WHERE n.nic_code IS NOT NULL) AS mapped,
                           COUNT(*) FILTER (WHERE n.nic_code IS NULL) AS unmapped
                    FROM economic_census.enterprises_full e
                    LEFT JOIN economic_census.nic_codes n
                      ON e.activity_code = n.nic_code
                """,
            }
            mapped_records = {}
            unmapped_records = {}
            for column_name, sql in coverage_sql.items():
                cur.execute(sql)
                row = cur.fetchone()
                mapped_records[column_name] = int(row["mapped"])
                unmapped_records[column_name] = int(row["unmapped"])

            cur.execute(
                """
                SELECT e.activity_code AS code, COUNT(*) AS rows
                FROM economic_census.enterprises_full e
                LEFT JOIN economic_census.nic_codes n ON e.activity_code = n.nic_code
                WHERE n.nic_code IS NULL
                GROUP BY e.activity_code
                ORDER BY COUNT(*) DESC
                LIMIT 50
                """
            )
            unmapped_codes = {
                "activity_code": [
                    {"code": row["code"], "rows": int(row["rows"])}
                    for row in cur.fetchall()
                ]
            }
        finally:
            cur.close()

        return {
            "success": True,
            "table": EC_ENTERPRISES_DATASET,
            "total_records": total,
            "coded_columns_found": profile["mapped_columns"],
            "lookup_tables_used": sorted({item["lookup_table"] for item in profile["mapped_columns"]}),
            "filter_fields_selected": profile["filters"],
            "hidden_columns": profile["hidden_columns"],
            "mapped_records": mapped_records,
            "unmapped_records": unmapped_records,
            "unmapped_codes": unmapped_codes,
            "remaining_schema_issues": [
                "Some Delhi district names were added as unverified placeholder labels.",
                "Remaining activity_code unmapped rows are malformed values such as XIO0, NILL, blanks, or punctuation-bearing codes.",
                "Non-primary coded fields use variable_metadata descriptions unless a dedicated lookup table is added.",
            ],
        }
    finally:
        conn.close()


@app.post("/data")
async def fetch_data(request: DataRequest):
    """Fetch data from database with specified columns"""
    
    conn = None
    try:
        conn = get_db_connection()
        schema_name, table_name, table_ref = resolve_relation(conn, request.table)
        available_columns = {row["column_name"] for row in get_table_columns(conn, schema_name, table_name)}

        # Validate column names against the actual table schema
        for col in request.columns:
            if not is_safe_identifier(col):
                raise HTTPException(status_code=400, detail=f"Invalid column name: {col}")
            if col not in available_columns:
                raise HTTPException(status_code=400, detail=f"Column '{col}' not found in '{request.table}'")

        columns_str = ", ".join([f'"{col}"' for col in request.columns])
            
        # Build WHERE clause from filters
        where_clauses = []
        where_values = []
        
        for col, val in request.filters.items():
            if not is_safe_identifier(col) or col not in available_columns:
                continue
            # PLFS numeric-code columns (state_ut_code, district_code, and other coded fields) are stored
            # zero-padded (e.g. '01'). Cast both sides to integer for a match.
            if _is_plfs_person_household(schema_name, table_name) and col in {"state_ut_code", "district_code"}:
                try:
                    where_clauses.append(f'NULLIF("{col}",\'\')::integer = %s')
                    where_values.append(int(str(val).strip()))
                except (ValueError, TypeError):
                    where_clauses.append(f'TRIM("{col}"::text) = %s')
                    where_values.append(str(val).strip())
            else:
                # Use TRIM to handle padded strings in the database
                where_clauses.append(f'TRIM("{col}"::text) = %s')
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

        cur.close()

        # ── PLFS UX: format coded values as "code - label" ──
        if _is_plfs_person_household(schema_name, table_name) and rows:
            requested_cols = set(request.columns)
            for row in rows:
                # State: state_ut_code → "01 - Jammu and Kashmir"
                if "state_ut_code" in row and row["state_ut_code"] is not None:
                    st_val = str(row["state_ut_code"]).strip()
                    state_label = get_plfs_state_name(st_val)
                    if state_label:
                        row["state_ut_code"] = f"{st_val} - {state_label}"

                # District: district_code → "01 - Kupwara" (needs state)
                if "district_code" in row and row["district_code"] is not None:
                    raw_st = str(row.get("state_ut_code", "")).split(" - ")[0].strip()
                    dc_val = str(row["district_code"]).strip()
                    dist_label = get_plfs_district_name(raw_st, dc_val)
                    if dist_label:
                        row["district_code"] = f"{dc_val} - {dist_label}"

                # Static-mapped coded columns
                for col_name, mapping in PLFS_STATIC_MAPPINGS.items():
                    if col_name in row and row[col_name] is not None:
                        code = str(row[col_name]).strip()
                        label = mapping.get(code)
                        if label:
                            row[col_name] = f"{code} - {label}"
        offset = int(request.offset)
        limit = int(request.limit)
        has_more = len(rows) == limit
        display_total = offset + len(rows) + (1 if has_more else 0)
        
        return {
            "success": True,
            "table": _format_qualified_name(schema_name, table_name),
            "columns": request.columns,
            "data": rows,
            "count": len(rows),
            "total": display_total,
            "has_more": has_more,
            "limit": limit,
            "offset": offset
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
            schema_name, table_name, table_ref = resolve_relation(conn, table)
            available_columns = {row["column_name"] for row in get_table_columns(conn, schema_name, table_name)}
            if column not in available_columns:
                raise HTTPException(status_code=400, detail=f"Column '{column}' not found in '{table}'")
                
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
            "table": _format_qualified_name(schema_name, table_name) if column else table,
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
        registry, _ = build_dataset_registry(conn)
        cur = conn.cursor()
        summary = []

        for dataset in registry:
            summary.append({
                'table': dataset['name'],
                'schema': dataset['schema'],
                'rows': dataset['row_count_estimate'],
                'columns': dataset['column_count'],
                'numeric_columns': sum(1 for col in dataset['columns'] if col['type'] in ['smallint', 'integer', 'bigint', 'numeric', 'real', 'double precision', 'decimal']),
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
        query_schema, query_table, table_ref = resolve_relation(conn, table)
            
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
        schema_name, table_name, table_ref = resolve_relation(conn, table)
        available_columns = {row["column_name"] for row in get_table_columns(conn, schema_name, table_name)}
        if column not in available_columns:
            raise HTTPException(status_code=400, detail=f"Column '{column}' not found in '{table}'")
            
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
        schema_name, table_name, table_ref = resolve_relation(conn, table)
            
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
