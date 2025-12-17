"""
Simple script to load sample census data
"""
import pandas as pd
from app.database import SessionLocal, init_db
from app.models.dataset import CensusData

def load_sample_data():
    """Load sample census data from CSV"""
    # Ensure tables exist
    print("Initializing database tables...")
    init_db()
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_count = db.query(CensusData).count()
        if existing_count > 0:
            print(f"Data already loaded ({existing_count} records). Skipping...")
            return
        
        # Read CSV
        df = pd.read_csv('data/sample_census_data.csv')
        print(f"Loading {len(df)} census records...")
        
        # Convert to model instances
        records = []
        for _, row in df.iterrows():
            record = CensusData(
                state=row['state'],
                district=row['district'],
                gender=row['gender'],
                age_group=row['age_group'],
                population=int(row['population']),
                literacy_rate=float(row['literacy_rate']),
                employment_rate=float(row['employment_rate']),
                year=int(row['year'])
            )
            records.append(record)
        
        # Bulk insert
        db.bulk_save_objects(records)
        db.commit()
        
        print(f"✓ Successfully loaded {len(records)} census records!")
        
    except Exception as e:
        print(f"Error loading data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    load_sample_data()
