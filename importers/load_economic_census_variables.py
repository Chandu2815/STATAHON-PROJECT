from sqlalchemy import create_engine, text

DATABASE_URL = (
    "postgresql+psycopg2://statahon_user:Statahon%40123@localhost:5432/statahon_db"
)

engine = create_engine(DATABASE_URL)

LEVEL_ID = 28

variables = [
    "sector",
    "state_ut",
    "district",
    "tehsil_taluka",
    "development_block",
    "village_town",
    "sub_town",
    "ward_mohalla",
    "enumeration_block_no",
    "additional_enumeration_block_no",
    "enterprise_with_premises_no",
    "enterprise_without_premises_no",
    "activity_code",
    "major_activity_code",
    "classification_of_enterprise",
    "nature_of_operation",
    "type_of_ownership",
    "social_group_of_owner",
    "power_fuel_used",
    "males_total",
    "females_total",
    "total_workers",
    "males_hired",
    "females_hired",
    "total_hired",
    "directory_non_directory",
    "oae_est_code",
    "big_city_code",
    "employment_size_class_type1",
    "employment_size_class_type2",
    "update_code",
    "nature_of_economic_activity_code",
    "tehsil_town_code",
    "village_ward_code",
    "file_code"
]

with engine.begin() as conn:

    for variable in variables:

        conn.execute(
            text("""
                INSERT INTO survey_variables
                (level_id, column_name, data_type)
                VALUES
                (:level_id, :column_name, 'text')
            """),
            {
                "level_id": LEVEL_ID,
                "column_name": variable
            }
        )

print(f"Inserted {len(variables)} variables")
