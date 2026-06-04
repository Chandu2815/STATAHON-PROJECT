from sqlalchemy import create_engine, text
import pandas as pd

engine = create_engine(
    "postgresql+psycopg2://statahon_user:Statahon%40123@localhost:5432/statahon_db"
)

csv_file = "/root/HCES_Data_2023-24_Csv/HCES_Data_2023-24_Csv/LEVEL - 01(Section 1 and 1_1).csv"

print("Loading CSV...")

df = pd.read_csv(csv_file)

df.columns = [c.strip().lower() for c in df.columns]

print(f"Rows: {len(df)}")

df.to_sql(
    "hces_level_01_2023_24",
    engine,
    if_exists="append",
    index=False,
    method="multi",
    chunksize=5000
)

print("Import completed")