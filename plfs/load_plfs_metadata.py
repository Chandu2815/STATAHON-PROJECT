import pandas as pd
import psycopg2
from psycopg2 import sql

EXCEL_FILE = "/root/STATAHON-PROJECT/plfs/2. FV_Data_LayoutPLFS_2025.xlsx"

conn = psycopg2.connect(
    host="localhost",
    database="statahon_db",
    user="postgres",
    password="StrongPassword123"
)

cur = conn.cursor()

# Clear old metadata if re-running
cur.execute("TRUNCATE TABLE plfs.variable_metadata RESTART IDENTITY;")

SHEETS = ["CHHV1", "CPERV1"]

for sheet in SHEETS:
    print(f"Processing sheet: {sheet}")

    df = pd.read_excel(EXCEL_FILE, sheet_name=sheet)

    # Clean column names
    df.columns = [str(c).strip() for c in df.columns]

    for _, row in df.iterrows():

        variable_name = str(row.get("Field_Name", "")).strip()
        description = str(row.get("Full Name", "")).strip()

        start_pos = row.get("Byte Position (Start)")
        end_pos = row.get("Byte Position (End)")
        size = row.get("Field Length")
        remarks = str(row.get("Remarks", "")).strip()

        # Skip blank rows
        if variable_name in ("", "nan", "None"):
            continue

        try:
            start_pos = int(start_pos) if pd.notna(start_pos) else None
        except:
            start_pos = None

        try:
            end_pos = int(end_pos) if pd.notna(end_pos) else None
        except:
            end_pos = None

        try:
            size = int(size) if pd.notna(size) else None
        except:
            size = None

        cur.execute(
            """
            INSERT INTO plfs.variable_metadata
            (
                source_table,
                variable_name,
                description,
                start_pos,
                end_pos,
                size,
                remarks
            )
            VALUES (%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                sheet,
                variable_name,
                description,
                start_pos,
                end_pos,
                size,
                remarks
            )
        )

conn.commit()

cur.close()
conn.close()

print("=================================")
print("PLFS metadata loaded successfully")
print("Sheets loaded: CHHV1, CPERV1")
print("=================================")
