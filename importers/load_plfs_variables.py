import pandas as pd
from sqlalchemy import create_engine, text

engine = create_engine(
    "postgresql+psycopg2://statahon_user:Statahon%40123@localhost:5432/statahon_db"
)

files = [
    (16, "/root/PLFS_Data/chhv1.csv"),
    (17, "/root/PLFS_Data/cperv1.csv"),
]

with engine.begin() as conn:
    for level_id, file_path in files:
        print(f"\nProcessing Level {level_id}")

        df = pd.read_csv(file_path, nrows=5)

        count = 0

        for col in df.columns:
            conn.execute(
                text("""
                    INSERT INTO survey_variables
                    (level_id, column_name, data_type)
                    VALUES
                    (:level_id, :column_name, 'text')
                """),
                {
                    "level_id": level_id,
                    "column_name": col
                }
            )
            count += 1

        print(f"Inserted {count} variables")