"""
Database configuration and session management
"""
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings
import sys

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
    # PostgreSQL with proper connection pooling
    engine = create_engine(
        settings.DATABASE_URL,
        echo=settings.DATABASE_ECHO,
        pool_pre_ping=True,  # Test connections before using
        pool_size=10,
        max_overflow=20,
        connect_args={"connect_timeout": 10}
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
    """Initialize database tables with error handling"""
    try:
        print("[DB] Initializing database...")
        
        # Import all models to ensure they're registered
        from app.models import dataset, user
        from app.models.user import User, UserRole, OtpChallenge
        import bcrypt
        import pyotp
        
        # Create all tables
        print("[DB] Creating tables from models...")
        Base.metadata.create_all(bind=engine)
        print("[DB] ✅ Tables created successfully")
        
        # Ensure TOTP columns exist for backward compatibility
        _ensure_user_totp_columns()
        
        # Create or update default users
        db = SessionLocal()
        try:
            def ensure_user(username, email, full_name, password, role, credits):
                """Create or update user account"""
                try:
                    user = db.query(User).filter(User.username == username).first()
                    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    
                    if not user:
                        print(f"[USER] Creating {role} user: {username}...")
                        user = User(
                            username=username,
                            email=email,
                            full_name=full_name,
                            hashed_password=hashed,
                            password=password,
                            role=role,
                            is_active=True,
                            credits=credits,
                            totp_secret=pyotp.random_base32(),
                            totp_enabled=True,
                        )
                        db.add(user)
                        db.commit()
                        print(f"[USER] ✅ Created {username} (Password: {password})")
                    else:
                        # Update password to ensure it's correct
                        user.hashed_password = hashed
                        user.password = password
                        if not user.totp_secret:
                            user.totp_secret = pyotp.random_base32()
                        user.totp_enabled = True
                        db.commit()
                        print(f"[USER] ✅ User {username} exists - password reset to: {password}")
                    return user
                except Exception as e:
                    print(f"[USER] ❌ Error creating user {username}: {str(e)}")
                    db.rollback()
                    raise
            
            # Create admin user
            ensure_user(
                username="admin",
                email="admin@mospi.gov.in",
                full_name="System Administrator",
                password="admin123",
                role=UserRole.ADMIN,
                credits=999999.0
            )
            
            # Create test user
            ensure_user(
                username="testuser",
                email="testuser@mospi.gov.in",
                full_name="Test User",
                password="test123",
                role=UserRole.RESEARCHER,
                credits=100.0
            )
            
            # Load CSV data if needed
            load_csv_data_if_needed(db)
            
        except Exception as e:
            print(f"[USER] ❌ Fatal error during user initialization: {str(e)}")
            db.rollback()
            raise
        finally:
            db.close()
            
        print("[DB] ✅ Database initialization complete")
        
    except Exception as e:
        print(f"[DB] ❌ CRITICAL: Database initialization failed")
        print(f"[DB] Error: {str(e)}")
        print(f"[DB] Type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
        # Create test user for demo
        ensure_user(
            username="testuser",
            email="testuser@mospi.gov.in",
            full_name="Test User",
            password="test123",
            role=UserRole.RESEARCHER,
            credits=100.0
        )
        
        # Auto-load CSV data if tables are empty
        load_csv_data_if_needed(db)
    finally:
        db.close()


def load_hces_datasets(db):
    """Load HCES (Household Consumption Expenditure Survey) datasets"""
    from sqlalchemy import text, inspect
    from pathlib import Path
    import pandas as pd
    from app.models.dataset import Dataset
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    base_path = Path(__file__).parent.parent
    
    hces_datasets = [
        {
            'name': 'HCES Household Identification',
            'table_name': 'hces_household_identification',
            'csv_file': 'hces_household_identification_clean.csv',
            'description': 'HCES Household Identification data'
        },
        {
            'name': 'HCES Food Expenditure',
            'table_name': 'hces_food_expenditure',
            'csv_file': 'hces_food_expenditure_clean.csv',
            'description': 'HCES Food Expenditure data'
        },
        {
            'name': 'HCES Non-Food Expenditure',
            'table_name': 'hces_non_food_expenditure',
            'csv_file': 'hces_non_food_expenditure_clean.csv',
            'description': 'HCES Non-Food Expenditure data'
        }
    ]
    
    for hces in hces_datasets:
        csv_path = base_path / hces['csv_file']
        if csv_path.exists():
            with engine.connect() as conn:
                if hces['table_name'] in tables:
                    count = conn.execute(text(f"SELECT COUNT(*) FROM {hces['table_name']}")).fetchone()[0]
                else:
                    count = 0
                
                if count == 0:
                    print(f"📊 Loading {hces['name']} from CSV...")
                    try:
                        df = pd.read_csv(csv_path)
                        df.to_sql(hces['table_name'], engine, if_exists='replace', index=False)
                        print(f"✅ Loaded {len(df):,} records into {hces['table_name']}")
                        
                        # Register dataset
                        existing = db.query(Dataset).filter(Dataset.table_name == hces['table_name']).first()
                        if not existing:
                            dataset = Dataset(
                                name=hces['name'],
                                description=f"{hces['description']} ({len(df):,} records)",
                                table_name=hces['table_name'],
                                config={"source": "MoSPI", "survey_type": "HCES", "record_count": len(df)}
                            )
                            db.add(dataset)
                            db.commit()
                    except Exception as e:
                        print(f"❌ Error loading {hces['name']}: {e}")
                else:
                    print(f"✅ {hces['name']} already has {count:,} records")


def load_csv_data_if_needed(db):
    """Load CSV data into database if tables are empty"""
    try:
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
        
        # Load HCES datasets (3, 4, 5)
        load_hces_datasets(db)
        
    except Exception as e:
        print(f"⚠️ CSV loading skipped due to error: {e}")


def _ensure_user_totp_columns() -> None:
    """Add TOTP columns for existing databases without running migrations."""
    inspector = inspect(engine)
    if "users" not in inspector.get_table_names():
        return

    user_columns = {col["name"] for col in inspector.get_columns("users")}

    with engine.begin() as conn:
        if "totp_secret" not in user_columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN totp_secret VARCHAR(64)"))
        if "totp_enabled" not in user_columns:
            conn.execute(text("ALTER TABLE users ADD COLUMN totp_enabled BOOLEAN DEFAULT FALSE"))


if __name__ == "__main__":
    print("Initializing database...")
    init_db()
    print("Database initialized successfully!")
