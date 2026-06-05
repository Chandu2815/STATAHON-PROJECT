import sqlalchemy
from sqlalchemy import text, inspect
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("DATABASE_URL not found in .env file. Exiting.")
    exit()

if not DATABASE_URL.startswith("postgresql"):
    print(f"Database URL '{DATABASE_URL}' is not for PostgreSQL. Exiting.")
    exit()

engine = sqlalchemy.create_engine(DATABASE_URL)

# Define the expected columns based on the SQLAlchemy model
# (type, nullable, default)
EXPECTED_COLUMNS = {
    "id": ("INTEGER", False, None),
    "email": ("VARCHAR(255)", False, None),
    "username": ("VARCHAR(100)", False, None),
    "hashed_password": ("VARCHAR(255)", False, None),
    "password": ("VARCHAR(255)", True, None),
    "full_name": ("VARCHAR(255)", True, None),
    "role": ("VARCHAR", False, "public"), # Enum is represented as VARCHAR
    "is_active": ("BOOLEAN", True, "true"),
    "credits": ("DOUBLE PRECISION", True, "0.0"),
    "created_by": ("INTEGER", True, None),
    "totp_secret": ("VARCHAR(64)", True, None),
    "totp_enabled": ("BOOLEAN", True, "false"),
    "created_at": ("TIMESTAMP WITH TIME ZONE", True, None), # server_default is not checked here
    "updated_at": ("TIMESTAMP WITH TIME ZONE", True, None) # onupdate is not checked here
}

def get_current_schema(inspector, table_name):
    """Get the current schema for a table."""
    columns = inspector.get_columns(table_name)
    return {c['name']: c for c in columns}

def run_migration():
    """Adds missing columns to the users table."""
    print("Connecting to the database...")
    try:
        with engine.connect() as connection:
            print("Connection successful.")
            
            inspector = inspect(engine)
            table_name = 'users'

            if not inspector.has_table(table_name):
                print(f"Table '{table_name}' does not exist. Please run initial setup.")
                return

            print(f"\n--- Current '{table_name}' table structure ---")
            current_columns = get_current_schema(inspector, table_name)
            for col_name, col_info in current_columns.items():
                print(f"- {col_name}: {col_info['type']}")

            missing_columns = set(EXPECTED_COLUMNS.keys()) - set(current_columns.keys())

            if not missing_columns:
                print("\nSchema is up to date. No migration needed.")
                return

            print("\n--- Missing columns found ---")
            for col in sorted(list(missing_columns)):
                print(f"- {col}")

            print("\n--- Generating and executing SQL ---")
            with connection.begin():
                for col_name in sorted(list(missing_columns)):
                    col_type, nullable, default = EXPECTED_COLUMNS[col_name]
                    
                    # Simplified for this script
                    if col_name == 'role':
                        sql = f"ALTER TABLE {table_name} ADD COLUMN {col_name} VARCHAR(50) {'NOT NULL' if not nullable else ''} DEFAULT '{default}'"
                    elif col_name == 'is_active':
                         sql = f"ALTER TABLE {table_name} ADD COLUMN {col_name} BOOLEAN DEFAULT {default}"
                    elif col_name == 'credits':
                         sql = f"ALTER TABLE {table_name} ADD COLUMN {col_name} DOUBLE PRECISION DEFAULT {default}"
                    elif col_name == 'totp_enabled':
                         sql = f"ALTER TABLE {table_name} ADD COLUMN {col_name} BOOLEAN DEFAULT {default}"
                    else:
                        sql = f"ALTER TABLE {table_name} ADD COLUMN {col_name} {col_type}"

                    print(f"Executing: {sql}")
                    connection.execute(text(sql))

                    if col_name == 'username':
                        print("Populating 'username' with email values...")
                        connection.execute(text('UPDATE users SET username = email'))
                        print("Setting 'username' column to NOT NULL and UNIQUE...")
                        connection.execute(text('ALTER TABLE users ALTER COLUMN username SET NOT NULL'))
                        connection.execute(text('ALTER TABLE users ADD CONSTRAINT uq_users_username UNIQUE (username)'))

            print("\nMigration applied successfully!")

    except sqlalchemy.exc.SQLAlchemyError as e:
        print(f"\nAn error occurred during migration: {e}")
    except Exception as e:
        print(f"\nAn unexpected error occurred: {e}")

if __name__ == "__main__":
    run_migration()
