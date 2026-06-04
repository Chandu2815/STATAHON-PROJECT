import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg2://statahon_user:Statahon%40123@localhost:5432/statahon_db"
)

csv_file = "/root/HCES_Data_2023-24_Csv/HCES_Data_2023-24_Csv/LEVEL - 01(Section 1 and 1_1).csv"

df = pd.read_csv(csv_file, nrows=100)

df.columns = [
    c.strip().lower().replace(" ", "_")
    for c in df.columns
]

df.head(0).to_sql(
    "hces_level_01_2023_24",
    engine,
    if_exists="replace",
    index=False
)

print("Table created successfully")