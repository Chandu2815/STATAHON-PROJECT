import pandas as pd
import psycopg2

conn = psycopg2.connect(
    dbname="statahon_db",
    user="postgres"
)

cur = conn.cursor()

# STATES
states = pd.read_excel(
    "/tmp/4. Indian_States_and_UTs_Code  Name.xlsx"
)

cur.execute("TRUNCATE plfs.state_codes;")

for _, row in states.iterrows():
    cur.execute(
        """
        INSERT INTO plfs.state_codes
        (state_code,state_name)
        VALUES (%s,%s)
        """,
        (
            int(row["State Code"]),
            str(row["State/UT Name"])
        )
    )

# DISTRICTS
districts = pd.read_excel(
   "/tmp/5. Indian_Districts_Code  Name.xlsx"
)

cur.execute("TRUNCATE plfs.district_codes;")

for _, row in districts.iterrows():
    cur.execute(
        """
        INSERT INTO plfs.district_codes
        (state_code,district_code,district_name)
        VALUES (%s,%s,%s)
        """,
        (
            int(row["State Code"]),
            int(row["District Code"]),
            str(row["District Name"])
        )
    )

conn.commit()

print("Loaded state and district mappings")

cur.close()
conn.close()
