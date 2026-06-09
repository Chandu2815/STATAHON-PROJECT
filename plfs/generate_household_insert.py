import psycopg2

conn = psycopg2.connect(dbname="statahon_db", user="postgres")
cur = conn.cursor()

cur.execute("""
SELECT variable_name, start_pos, size
FROM plfs.variable_metadata
WHERE source_table='CHHV1'
ORDER BY start_pos
""")

cols = []
exprs = []

for var, start, size in cur.fetchall():
    cols.append(f'"{var}"')
    exprs.append(
        f'TRIM(SUBSTRING(raw_record FROM {start} FOR {size}))'
    )

sql = f"""
INSERT INTO plfs.household
({','.join(cols)})
SELECT
{','.join(exprs)}
FROM plfs.household_raw;
"""

with open("/tmp/load_household.sql", "w") as f:
    f.write(sql)

print("Generated /tmp/load_household.sql")
