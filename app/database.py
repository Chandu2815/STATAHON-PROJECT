"""
Database configuration and session management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

settings = get_settings()

# Create database engine
# Support both PostgreSQL and SQLite
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        connect_args=connect_args
    )
else:
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        pool_pre_ping=True,
        pool_size=10,
        max_overflow=20
    )

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for models
Base = declarative_base()


def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables"""
    # Import all models to ensure they're registered
    from app.models import dataset, user
    from app.models.user import User, UserRole
    import bcrypt
    
    Base.metadata.create_all(bind=engine)
    
    # Create default admin if not exists
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if not admin:
            admin = db.query(User).filter(User.username == 'admin').first()
        
        if not admin:
            print("Creating default admin user...")
            password = "admin123"
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            admin = User(
                username="admin",
                email="admin@mospi.gov.in",
                full_name="System Administrator",
                hashed_password=hashed.decode('utf-8'),
                password=password,  # Store plain password for admin viewing
                role=UserRole.ADMIN,
                is_active=True,
                credits=999999.0
            )
            db.add(admin)
            db.commit()
            print(f"✅ Default admin created - Username: admin, Password: admin123")
        else:
            print(f"✅ Admin user exists: {admin.username}")
        
        # Auto-load CSV data if tables are empty
        load_csv_data_if_needed(db)
    finally:
        db.close()


def load_csv_data_if_needed(db):
    """Load CSV data into database if tables are empty"""
    from sqlalchemy import text, inspect
    from pathlib import Path
    import pandas as pd
    from app.models.dataset import Dataset
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    # Check if household_survey table exists and has data
    base_path = Path(__file__).parent.parent
    
    # Load Household Survey (chhv1.csv)
    csv_path = base_path / "chhv1.csv"
    if csv_path.exists():
        with engine.connect() as conn:
            if 'household_survey' in tables:
                count = conn.execute(text("SELECT COUNT(*) FROM household_survey")).fetchone()[0]
            else:
                count = 0
            
            if count == 0:
                print("📊 Loading Household Survey data from CSV...")
                try:
                    df = pd.read_csv(csv_path)
                    # Rename columns to match database schema
                    column_mapping = {
                        'Panel': 'Panel', 'File Identification': 'File_Identification',
                        'Schdule': 'Schdule', 'Quarter': 'Quarter', 'Visit': 'Visit',
                        'Sector': 'Sector', 'State/ UT Code': 'State_Ut_Code',
                        'District Code': 'District_Code', 'NSS Region': 'NSS_Region',
                        'Stratum': 'Stratum', 'Sub-Stratum': 'Sub_Stratum',
                        'Sub-Sample': 'Sub_Sample', 'FOD Sub Region': 'Fod_Sub_Region',
                        'FSU': 'FSU', 'Sample Sg/Sb No.': 'Sample_Sg_Sb_No',
                        'Second Stage Stratum No.': 'Second_Stage_Stratum_No',
                        'Sample Household Number': 'Sample_Household_Number',
                        'Month of Survey': 'Month_of_Survey', 'Response Code': 'Response_Code',
                        'Survey Code': 'Survey_Code', 'Reason for Substitution': 'Reason_for_Substitution',
                        'Household Size': 'Household_Size', 'Household Type': 'Household_Type',
                        'Religion': 'Religion', 'Social Group': 'Social_Group',
                        'Usual Expenditure': 'Usual_Expenditure',
                        'Imputed Homegrown Consumption': 'Imputed_Homegrown_Consumption',
                        'Imputed Wages Consumption': 'Imputed_Wages_Consumption',
                        'Annual Clothing Expenditure': 'Annual_Clothing_Expenditure',
                        'Annual Durables Expenditure': 'Annual_Durables_Expenditure',
                        'Monthly Consumer Expenditure': 'Monthly_Consumer_Expenditure',
                        'Informant Serial No.': 'Informant_Serial_No', 'Survey Date': 'Survey_Date',
                        'Total Time Taken': 'Total_Time_Taken',
                        'NSS Sector, Stratum, Substr., Subsam.': 'NSS_Sector_Stratum_Substr_Subsam',
                        'NSC (Sector, Stratum, Substr.)': 'NSC_Sector_Stratum_Substr',
                        'Subsample Multiplier': 'Subsample_Multiplier',
                        'Contrib. to Sample Count': 'Contrib_Sample_Count'
                    }
                    df = df.rename(columns=column_mapping)
                    df.to_sql('household_survey', engine, if_exists='replace', index=False)
                    print(f"✅ Loaded {len(df):,} household records")
                    
                    # Register dataset
                    existing = db.query(Dataset).filter(Dataset.table_name == 'household_survey').first()
                    if not existing:
                        dataset = Dataset(
                            name="PLFS Household Survey",
                            description=f"Periodic Labour Force Survey (PLFS) Household-level data ({len(df):,} records)",
                            table_name="household_survey",
                            config={"source": "MoSPI", "survey_type": "PLFS", "record_count": len(df)}
                        )
                        db.add(dataset)
                        db.commit()
                except Exception as e:
                    print(f"❌ Error loading household data: {e}")
            else:
                print(f"✅ Household Survey already has {count:,} records")
    
    # Load Person Survey (cperv1.csv or cperv1_sample.csv)
    csv_path = base_path / "cperv1_sample.csv"  # Use sample for production
    if not csv_path.exists():
        csv_path = base_path / "cperv1.csv"  # Fallback to full file
    if csv_path.exists():
        with engine.connect() as conn:
            if 'person_survey' in tables:
                count = conn.execute(text("SELECT COUNT(*) FROM person_survey")).fetchone()[0]
            else:
                count = 0
            
            if count == 0:
                print("📊 Loading Person Survey data from CSV...")
                try:
                    df = pd.read_csv(csv_path)  # Load all rows from sample file
                    # Rename columns
                    column_mapping = {
                        'Panel': 'Panel', 'File Identification': 'File_Identification',
                        'Schdule': 'Schdule', 'Quarter': 'Quarter', 'Visit': 'Visit',
                        'Sector': 'Sector', 'State/ UT Code': 'State_UT_Code',
                        'District Code': 'District_Code', 'Person Serial No.': 'Person_Serial_No',
                        'Relation to Head': 'Relation_to_Head', 'Sex': 'Sex', 'Age': 'Age',
                        'Marital Status': 'Marital_Status', 'General Education': 'General_Education',
                        'Technical Education': 'Technical_Education',
                        'Vocational Training': 'Vocational_Training',
                        'Usual Activity Status (ps)': 'Usual_Activity_Status_PS',
                        'Usual Activity NIC (ps)': 'Usual_Activity_NIC_PS',
                        'Usual Activity NCO (ps)': 'Usual_Activity_NCO_PS',
                        'Usual Activity Status (ss)': 'Usual_Activity_Status_SS',
                        'Usual Activity NIC (ss)': 'Usual_Activity_NIC_SS',
                        'Usual Activity NCO (ss)': 'Usual_Activity_NCO_SS',
                        'Curr. Week Activity Status': 'Curr_Week_Activity_Status',
                        'Curr. Week Activity NIC': 'Curr_Week_Activity_NIC',
                        'Curr. Week Activity NCO': 'Curr_Week_Activity_NCO',
                        'Total Earnings Received': 'Total_Earnings_Received'
                    }
                    df = df.rename(columns=column_mapping)
                    df.to_sql('person_survey', engine, if_exists='replace', index=False)
                    print(f"✅ Loaded {len(df):,} person records")
                    
                    # Register dataset
                    existing = db.query(Dataset).filter(Dataset.table_name == 'person_survey').first()
                    if not existing:
                        dataset = Dataset(
                            name="PLFS Person Survey Data",
                            description=f"Periodic Labour Force Survey (PLFS) Person-level data ({len(df):,} records)",
                            table_name="person_survey",
                            config={"source": "MoSPI", "survey_type": "PLFS", "record_count": len(df)}
                        )
                        db.add(dataset)
                        db.commit()
                except Exception as e:
                    print(f"❌ Error loading person data: {e}")
            else:
                print(f"✅ Person Survey already has {count:,} records")


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialized successfully!")
