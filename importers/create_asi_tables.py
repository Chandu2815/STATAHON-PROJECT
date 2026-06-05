import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg2://statahon_user:Statahon%40123@localhost:5432/statahon_db"
)

files = [
    ("asi_block_a_2023_24", "/root/ASI_Data/ASI_DATA_2023_24_CSV/blkA202324.csv"),
    ("asi_block_b_2023_24", "/root/ASI_Data/ASI_DATA_2023_24_CSV/blkB202324.csv"),
    ("asi_block_c_2023_24", "/root/ASI_Data/ASI_DATA_2023_24_CSV/blkC202324.csv"),
    ("asi_block_d_2023_24", "/root/ASI_Data/ASI_DATA_2023_24_CSV/blkD202324.csv"),
    ("asi_block_e_2023_24", "/root/ASI_Data/ASI_DATA_2023_24_CSV/blkE202324.csv"),
    ("asi_block_f_2023_24", "/root/ASI_Data/ASI_DATA_2023_24_CSV/blkF202324.csv"),
    ("asi_block_g_2023_24", "/root/ASI_Data/ASI_DATA_2023_24_CSV/blkG202324.csv"),
    ("asi_block_h_2023_24", "/root/ASI_Data/ASI_DATA_2023_24_CSV/blkH202324.csv"),
    ("asi_block_i_2023_24", "/root/ASI_Data/ASI_DATA_2023_24_CSV/blkI202324.csv"),
    ("asi_block_j_2023_24", "/root/ASI_Data/ASI_DATA_2023_24_CSV/blkJ202324.csv"),
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
