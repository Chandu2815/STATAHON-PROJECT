import pandas as pd
import re
from pathlib import Path
from sqlalchemy import create_engine, text

# ==========================
# CONFIG
# ==========================

SURVEY_NAME = "HCES"
SURVEY_YEAR = "2023-24"

DATA_FOLDER = Path(
    "/root/HCES_Data_2023-24_Csv/HCES_Data_2023-24_Csv"
)

DATABASE_URL = (
    "postgresql+psycopg2://statahon_user:Statahon%40123@localhost:5432/statahon_db"
)

engine = create_engine(DATABASE_URL)

# ==========================
# GET LEVEL NUMBER
# ==========================

def get_level_number(filename):
    match = re.search(r'LEVEL\s*-\s*(\d+)', filename, re.IGNORECASE)

    if not match:
        match = re.search(r'Level\s*-\s*(\d+)', filename)

    return int(match.group(1))


# ==========================
# REGISTER VARIABLES
# ==========================

files = sorted(DATA_FOLDER.glob("*.csv"))

with engine.begin() as conn:

    for csv_file in files:

        level_no = get_level_number(csv_file.name)

        print(f"\nProcessing Level {level_no}")

        columns = pd.read_csv(
            csv_file,
            nrows=0
        ).columns.tolist()

        result = conn.execute(
            text("""
                SELECT level_id
                FROM survey_levels
                WHERE level_no = :level_no
            """),
            {"level_no": level_no}
        )

        row = result.fetchone()

        if not row:
            print(f"Level {level_no} not found")
            continue

        level_id = row[0]

        for col in columns:

            conn.execute(
                text("""
                    INSERT INTO survey_variables
                    (level_id, column_name, data_type)
                    VALUES
                    (:level_id, :column_name, 'UNKNOWN')
                """),
                {
                    "level_id": level_id,
                    "column_name": col
                }
            )

        print(
            f"Inserted {len(columns)} variables"
        )

print("\nDone.")