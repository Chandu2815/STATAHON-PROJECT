from pathlib import Path
from sqlalchemy import create_engine, text

engine = create_engine(
    "postgresql+psycopg2://statahon_user:Statahon%40123@localhost:5432/statahon_db"
)

files = [
    ("asi_block_a_2023_24", Path("/root/ASI_Data/ASI_DATA_2023_24_CSV/blkA202324.csv")),
    ("asi_block_b_2023_24", Path("/root/ASI_Data/ASI_DATA_2023_24_CSV/blkB202324.csv")),
    ("asi_block_c_2023_24", Path("/root/ASI_Data/ASI_DATA_2023_24_CSV/blkC202324.csv")),
    ("asi_block_d_2023_24", Path("/root/ASI_Data/ASI_DATA_2023_24_CSV/blkD202324.csv")),
    ("asi_block_e_2023_24", Path("/root/ASI_Data/ASI_DATA_2023_24_CSV/blkE202324.csv")),
    ("asi_block_f_2023_24", Path("/root/ASI_Data/ASI_DATA_2023_24_CSV/blkF202324.csv")),
    ("asi_block_g_2023_24", Path("/root/ASI_Data/ASI_DATA_2023_24_CSV/blkG202324.csv")),
    ("asi_block_h_2023_24", Path("/root/ASI_Data/ASI_DATA_2023_24_CSV/blkH202324.csv")),
    ("asi_block_i_2023_24", Path("/root/ASI_Data/ASI_DATA_2023_24_CSV/blkI202324.csv")),
    ("asi_block_j_2023_24", Path("/root/ASI_Data/ASI_DATA_2023_24_CSV/blkJ202324.csv")),
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

print("\nASI Import Complete!")
