from pathlib import Path
from sqlalchemy import create_engine, text

engine = create_engine(
    "postgresql+psycopg2://statahon_user:Statahon%40123@localhost:5432/statahon_db"
)

files = [
    (
        "plfs_household_2023_24",
        Path("/root/PLFS_Data/chhv1.csv")
    ),
    (
        "plfs_person_2023_24",
        Path("/root/PLFS_Data/cperv1.csv")
    )
]

for table_name, csv_file in files:

    print(f"\nImporting {table_name}")

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

print("\nPLFS Import Complete!")
