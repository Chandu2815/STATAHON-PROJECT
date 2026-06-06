from sqlalchemy import create_engine, text

engine = create_engine(
    "postgresql+psycopg2://statahon_user:Statahon%40123@localhost:5432/statahon_db"
)

with engine.begin() as conn:

    conn.execute(
        text("""
            INSERT INTO economic_census_1990_enterprise
            (
                sector,
                state_ut,
                district,
                activity_code,
                major_activity_code,
                file_code
            )
            VALUES
            (
                '1',
                '02',
                '01',
                '6500',
                '07',
                'EC'
            )
        """)
    )

print("Inserted test row")
