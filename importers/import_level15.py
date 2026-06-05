from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg2://statahon_user:Statahon%40123@localhost:5432/statahon_db"
)

csv_file = "/root/HCES_Data_2023-24_Csv/HCES_Data_2023-24_Csv/LEVEL - 15 (Section 1_1, A2,B2  C2).csv"

table_name = "hces_level_15_2023_24"

conn = engine.raw_connection()

try:
    cur = conn.cursor()

    with open(csv_file, "r", encoding="utf-8") as f:
        cur.copy_expert(
            f"""
            COPY {table_name}
            FROM STDIN
            WITH CSV HEADER
            """,
            f
        )

    conn.commit()

finally:
    conn.close()

print("Level 15 imported successfully")