import psycopg2

conn = psycopg2.connect(
    host="localhost",
    dbname="statahon_db",
    user="ec_user",
    password="StrongPassword123"
)

cur = conn.cursor()

cur.execute("""
SELECT record_text
FROM economic_census.enterprises_raw
""")

rows = cur.fetchall()

for (r,) in rows:

    cur.execute("""
    INSERT INTO economic_census.enterprises_parsed (
        sector,
        state_code,
        district_code,
        tehsil_code,
        development_block,
        village_town,
        sub_town,
        ward_hamlet_code,
        activity_code,
        major_activity_code,
        enterprise_classification,
        nature_of_operation,
        ownership_type,
        social_group_owner,
        power_fuel_used,
        male_workers_total,
        female_workers_total,
        total_workers,
        male_hired_workers,
        female_hired_workers,
        total_hired_workers,
        directory_non_directory,
        oae_est_code,
        big_city_code,
        employment_size_class_1,
        employment_size_class_2,
        nature_of_economic_activity_code
    )
    VALUES (
        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
        %s,%s,%s,%s,%s,%s,%s
    )
    """, (
        int(r[0:1].strip() or 0),      # sector (1)
        int(r[1:3].strip() or 0),      # state (2-3)
        int(r[3:5].strip() or 0),      # district (4-5)
        int(r[5:9].strip() or 0),      # tehsil (6-9)
        int(r[9:13].strip() or 0),     # development block (10-13)
        int(r[13:17].strip() or 0),    # village/town (14-17)
        int(r[17:20].strip() or 0),    # sub town (18-20)
        int(r[20:23].strip() or 0),    # ward/hamlet (21-23)
        r[36:40].strip(),              # activity code (37-40)
        int(r[40:42].strip() or 0),    # major activity (41-42)
        int(r[42:43].strip() or 0),    # classification (43)
        int(r[43:44].strip() or 0),    # nature operation (44)
        int(r[44:45].strip() or 0),    # ownership (45)
        int(r[45:46].strip() or 0),    # social group (46)
        r[46:47].strip(),              # power/fuel (47)
        int(r[47:52].strip() or 0),    # male workers (48-52)
        int(r[52:57].strip() or 0),    # female workers (53-57)
        int(r[57:63].strip() or 0),    # total workers (58-63)
        int(r[63:68].strip() or 0),    # male hired (64-68)
        int(r[68:73].strip() or 0),    # female hired (69-73)
        int(r[73:79].strip() or 0),    # total hired (74-79)
        int(r[79:80].strip() or 0),    # directory/non-directory (80)
        int(r[80:81].strip() or 0),    # OAE/EST (81)
        int(r[81:83].strip() or 0),    # big city code (82-83)
        int(r[83:84].strip() or 0),    # employment class 1 (84)
        int(r[84:86].strip() or 0),    # employment class 2 (85-86)
        int(r[87:90].strip() or 0)     # nature econ activity (88-90)
    ))

conn.commit()

print(f"Loaded {len(rows)} records")

cur.close()
conn.close()
