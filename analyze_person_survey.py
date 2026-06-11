from app.database import SessionLocal
from sqlalchemy import inspect, text

db = SessionLocal()
engine = db.bind

inspector = inspect(engine)
cols = inspector.get_columns('person_survey')

print("Person Survey Table Columns:")
print("=" * 70)
for c in cols:
    print(f"  {c['name']} ({c['type']})")

print(f"\n{'='*70}")
print("Sample query to test:")
print("  State: TELANGANA (need State_UT_Code = 36)")
print("  District: NIRMAL (need District_Code)")
print("  Gender: MALE (need Sex = 1)")
print("  Age: 15-29 (need Age between 15 and 29)")

with engine.connect() as conn:
    count = conn.execute(text("SELECT COUNT(*) FROM person_survey WHERE State_UT_Code = '36'")).fetchone()[0]
    print(f"  Records with State_UT_Code=36 (Telangana): {count}")

    districts = conn.execute(text("SELECT DISTINCT District_Code FROM person_survey WHERE State_UT_Code = '36' LIMIT 10")).fetchall()
    print(f"  Example Telangana district codes: {[d[0] for d in districts]}")

    nirmal_count = conn.execute(text("SELECT COUNT(*) FROM person_survey WHERE State_UT_Code = '36' AND District_Code = '04'")).fetchone()[0]
    print(f"  Records in Nirmal (code 04): {nirmal_count}")

    sex_values = conn.execute(text("SELECT DISTINCT Sex FROM person_survey LIMIT 5")).fetchall()
    print(f"  Sex values in table: {[s[0] for s in sex_values]}")

    age_range = conn.execute(text("SELECT MIN(Age), MAX(Age) FROM person_survey")).fetchone()
    print(f"  Age range: {age_range[0]} to {age_range[1]}")

db.close()
