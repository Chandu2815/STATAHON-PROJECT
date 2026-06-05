import re
from pathlib import Path
from sqlalchemy import create_engine, text

engine = create_engine(
    "postgresql+psycopg2://statahon_user:Statahon%40123@localhost:5432/statahon_db"
)

DATA_FOLDER = Path(
    "/root/HCES_Data_2023-24_Csv/HCES_Data_2023-24_Csv"
)

def get_level_number(filename):
    match = re.search(r'LEVEL\s*-\s*(\d+)', filename, re.IGNORECASE)

    if not match:
        match = re.search(r'Level\s*-\s*(\d+)', filename)

    return int(match.group(1))


files = sorted(DATA_FOLDER.glob("*.csv"))

for csv_file in files:

    level_no = get_level_number(csv_file.name)

    table_name = f"hces_level_{level_no:02d}_2023_24"

    with engine.connect() as conn:

        result = conn.execute(
            text("""
                SELECT row_count
                FROM survey_tables
                WHERE table_name = :table_name
            """),
            {"table_name": table_name}
        )

        row_count = result.fetchone()[0]

    if row_count > 0:
        print(f"Skipping {table_name}")
        continue

    print(f"Importing {table_name}")

    raw_conn = engine.raw_connection()

    try:

        cur = raw_conn.cursor()

        with open(csv_file, "r", encoding="utf-8") as f:

            cur.copy_expert(
                f"""
                COPY {table_name}
                FROM STDIN
                WITH CSV HEADER
                """,
                f
            )

        raw_conn.commit()

    finally:
        raw_conn.close()

    with engine.begin() as conn:

        result = conn.execute(
            text(f"SELECT COUNT(*) FROM {table_name}")
        )

        count = result.fetchone()[0]

        conn.execute(
            text("""
                UPDATE survey_tables
                SET row_count = :count
                WHERE table_name = :table_name
            """),
            {
                "count": count,
                "table_name": table_name
            }
        )

    print(f"{table_name}: {count} rows")