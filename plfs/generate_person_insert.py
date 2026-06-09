import psycopg2

conn = psycopg2.connect(
    dbname="statahon_db",
    user="postgres"
)

cur = conn.cursor()

cur.execute("""
SELECT variable_name, start_pos, size
FROM plfs.variable_metadata
WHERE source_table = 'CPERV1'
ORDER BY start_pos
""")

rows = cur.fetchall()

cols = []
exprs = []

for var_name, start_pos, size in rows:
    cols.append(f'"{var_name}"')
    exprs.append(
        f'TRIM(SUBSTRING(raw_record FROM {start_pos} FOR {size}))'
    )

sql = f"""
TRUNCATE TABLE plfs.person  RESTART IDENTITY;

INSERT INTO plfs.person
(
{','.join(cols)}
)
SELECT
{','.join(exprs)}
FROM plfs.person_raw;
"""

with open("/tmp/load_person.sql", "w") as f:
    f.write(sql)

print("Generated /tmp/load_person.sql")

cur.close()
conn.close()
