import os
import sys
import psycopg2
from psycopg2.extras import DictCursor

def run_etl():
    # Database connection parameters
    db_host = os.environ.get("DB_HOST", "187.127.138.4")
    db_port = os.environ.get("DB_PORT", "5432")
    db_name = os.environ.get("DB_NAME", "statahon_db")
    db_user = os.environ.get("DB_USER", "postgres")
    db_password = os.environ.get("DB_PASSWORD", "Statathon2026")
    
    print("Connecting to database...")
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            dbname=db_name,
            user=db_user,
            password=db_password
        )
        cur = conn.cursor(cursor_factory=DictCursor)
        
        # Aggregate male workers
        print("Extracting male workers data...")
        cur.execute("""
            SELECT 
                COALESCE(NULLIF(TRIM(state_name), ''), 'Unknown State') as state,
                COALESCE(NULLIF(TRIM(district_name), ''), 'Unknown District') as district,
                SUM(CAST(NULLIF(TRIM(male_workers_total), '') AS integer)) as population
            FROM economic_census.enterprise_view
            WHERE NULLIF(TRIM(male_workers_total), '') IS NOT NULL
              AND TRIM(male_workers_total) ~ '^[0-9]+$'
            GROUP BY state_name, district_name
        """)
        male_data = cur.fetchall()
        
        # Aggregate female workers
        print("Extracting female workers data...")
        cur.execute("""
            SELECT 
                COALESCE(NULLIF(TRIM(state_name), ''), 'Unknown State') as state,
                COALESCE(NULLIF(TRIM(district_name), ''), 'Unknown District') as district,
                SUM(CAST(NULLIF(TRIM(female_workers_total), '') AS integer)) as population
            FROM economic_census.enterprise_view
            WHERE NULLIF(TRIM(female_workers_total), '') IS NOT NULL
              AND TRIM(female_workers_total) ~ '^[0-9]+$'
            GROUP BY state_name, district_name
        """)
        female_data = cur.fetchall()
        
        # Clear existing census_data
        print("Clearing existing census_data table...")
        cur.execute("TRUNCATE TABLE public.census_data RESTART IDENTITY;")
        
        # Prepare insert query
        insert_query = """
            INSERT INTO public.census_data 
            (state, district, gender, age_group, population, literacy_rate, employment_rate, year, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
        """
        
        # Insert Male Data
        print(f"Inserting {len(male_data)} records for male workers...")
        male_records = []
        for row in male_data:
            state = row['state']
            district = row['district']
            population = row['population']
            if population is None:
                continue
                
            male_records.append((
                state, district, 'Male', 'All Ages', population, 0.0, 100.0, 1990
            ))
            
        if male_records:
            from psycopg2.extras import execute_batch
            execute_batch(cur, insert_query, male_records)
            
        # Insert Female Data
        print(f"Inserting {len(female_data)} records for female workers...")
        female_records = []
        for row in female_data:
            state = row['state']
            district = row['district']
            population = row['population']
            if population is None:
                continue
                
            female_records.append((
                state, district, 'Female', 'All Ages', population, 0.0, 100.0, 1990
            ))
            
        if female_records:
            from psycopg2.extras import execute_batch
            execute_batch(cur, insert_query, female_records)
            
        # Total
        print("Extracting total workers data for 'Total' gender...")
        cur.execute("""
            SELECT 
                COALESCE(NULLIF(TRIM(state_name), ''), 'Unknown State') as state,
                COALESCE(NULLIF(TRIM(district_name), ''), 'Unknown District') as district,
                SUM(CAST(NULLIF(TRIM(total_workers), '') AS integer)) as population
            FROM economic_census.enterprise_view
            WHERE NULLIF(TRIM(total_workers), '') IS NOT NULL
              AND TRIM(total_workers) ~ '^[0-9]+$'
            GROUP BY state_name, district_name
        """)
        total_data = cur.fetchall()
        
        total_records = []
        for row in total_data:
            state = row['state']
            district = row['district']
            population = row['population']
            if population is None:
                continue
                
            total_records.append((
                state, district, 'Total', 'All Ages', population, 0.0, 100.0, 1990
            ))
            
        if total_records:
            print(f"Inserting {len(total_records)} records for total workers...")
            execute_batch(cur, insert_query, total_records)
            
        conn.commit()
        print("Data successfully loaded into public.census_data!")
        
        cur.execute("SELECT COUNT(*) FROM public.census_data;")
        count = cur.fetchone()[0]
        print(f"Total rows in public.census_data: {count}")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        if 'conn' in locals() and conn:
            conn.rollback()
    finally:
        if 'cur' in locals() and cur:
            cur.close()
        if 'conn' in locals() and conn:
            conn.close()
            print("Database connection closed.")

if __name__ == "__main__":
    run_etl()
