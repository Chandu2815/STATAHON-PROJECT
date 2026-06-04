import pandas as pd
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

with engine.begin() as conn:

    for csv_file in files:

        level_no = get_level_number(csv_file.name)

        table_name = f"hces_level_{level_no:02d}_2023_24"

        print(f"Creating {table_name}")

        df = pd.read_csv(csv_file, nrows=100)

        df.columns = [
            c.strip().lower().replace(" ", "_")
            for c in df.columns
        ]

        df.head(0).to_sql(
            table_name,
            engine,
            if_exists="replace",
            index=False
        )

        result = conn.execute(
            text("""
                SELECT level_id
                FROM survey_levels
                WHERE level_no = :level_no
            """),
            {"level_no": level_no}
        )

        level_id = result.fetchone()[0]

        conn.execute(
            text("""
                INSERT INTO survey_tables
                (level_id, table_name)
                VALUES
                (:level_id, :table_name)
                ON CONFLICT DO NOTHING
            """),
            {
                "level_id": level_id,
                "table_name": table_name
            }
        )

print("Done")