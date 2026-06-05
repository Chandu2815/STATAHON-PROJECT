import pandas as pd
from pathlib import Path
from sqlalchemy import create_engine, text

# ==========================
# CONFIG
# ==========================

DATA_FOLDER = Path(
    "/root/ASI_Data/ASI_DATA_2023_24_CSV"
)

DATABASE_URL = (
    "postgresql+psycopg2://statahon_user:Statahon%40123@localhost:5432/statahon_db"
)

engine = create_engine(DATABASE_URL)

# ==========================
# ASI BLOCK → LEVEL NUMBER
# ==========================

def get_level_number(filename):

    mapping = {
        "blka": 1,
        "blkb": 2,
        "blkc": 3,
        "blkd": 4,
        "blke": 5,
        "blkf": 6,
        "blkg": 7,
        "blkh": 8,
        "blki": 9,
        "blkj": 10
    }

    filename = filename.lower()

    for key, value in mapping.items():
        if filename.startswith(key):
            return value

    raise ValueError(f"Unknown file: {filename}")


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
                WHERE round_id = 3
                AND level_no = :level_no
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

        print(f"Inserted {len(columns)} variables")

print("\nDone.")
