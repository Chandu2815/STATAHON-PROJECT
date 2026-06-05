import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg2://statahon_user:Statahon%40123@localhost:5432/statahon_db"
)

files = [
    ("plfs_household_2023_24", "/root/PLFS_Data/chhv1.csv"),
    ("plfs_person_2023_24", "/root/PLFS_Data/cperv1.csv")
]

for table_name, csv_file in files:

    cols = pd.read_csv(csv_file, nrows=0).columns

    columns_sql = []

    for col in cols:
        clean = (
            col.lower()
            .replace(" ", "_")
            .replace("-", "_")
            .replace("/", "_")
            .replace("(", "")
            .replace(")", "")
        )

        columns_sql.append(f'"{clean}" TEXT')

    sql = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        {",".join(columns_sql)}
    );
    """

    with engine.begin() as conn:
        conn.exec_driver_sql(sql)

    print(f"Created {table_name}")
