import psycopg2

conn = psycopg2.connect(
    host="localhost",
    dbname="statahon_db",
    user="ec_user",
    password="StrongPassword123"
)

cur = conn.cursor()

# Read metadata
cur.execute("""
SELECT variable_name, start_pos, end_pos
FROM economic_census.variable_metadata
ORDER BY start_pos
""")

metadata = cur.fetchall()

# Read raw records
cur.execute("""
SELECT record_text
FROM economic_census.enterprises_raw
""")

rows = cur.fetchall()

columns = [m[0] for m in metadata]
column_sql = ",".join(columns)
placeholders = ",".join(["%s"] * len(columns))

insert_sql = f"""
INSERT INTO economic_census.enterprises_full
({column_sql})
VALUES ({placeholders})
"""

count = 0

for (record,) in rows:

    values = []

    for _, start_pos, end_pos in metadata:
        value = record[start_pos - 1:end_pos].strip()
        values.append(value)

    cur.execute(insert_sql, values)

    count += 1

    if count % 1000 == 0:
        print(f"Loaded {count} records")

conn.commit()

print(f"Done. Loaded {count} records")

cur.close()
conn.close()
