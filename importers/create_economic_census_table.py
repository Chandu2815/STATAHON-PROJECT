from sqlalchemy import create_engine

engine = create_engine(
    "postgresql+psycopg2://statahon_user:Statahon%40123@localhost:5432/statahon_db"
)

sql = """
CREATE TABLE IF NOT EXISTS economic_census_1990_enterprise (

    sector TEXT,
    state_ut TEXT,
    district TEXT,
    tehsil_taluka TEXT,
    development_block TEXT,
    village_town TEXT,
    sub_town TEXT,
    ward_mohalla TEXT,
    enumeration_block_no TEXT,
    additional_enumeration_block_no TEXT,
    enterprise_with_premises_no TEXT,
    enterprise_without_premises_no TEXT,
    activity_code TEXT,
    major_activity_code TEXT,
    classification_of_enterprise TEXT,
    nature_of_operation TEXT,
    type_of_ownership TEXT,
    social_group_of_owner TEXT,
    power_fuel_used TEXT,
    males_total TEXT,
    females_total TEXT,
    total_workers TEXT,
    males_hired TEXT,
    females_hired TEXT,
    total_hired TEXT,
    directory_non_directory TEXT,
    oae_est_code TEXT,
    big_city_code TEXT,
    employment_size_class_type1 TEXT,
    employment_size_class_type2 TEXT,
    update_code TEXT,
    nature_of_economic_activity_code TEXT,
    tehsil_town_code TEXT,
    village_ward_code TEXT,
    file_code TEXT

);
"""

with engine.begin() as conn:
    conn.exec_driver_sql(sql)

print("Economic Census table created successfully")
