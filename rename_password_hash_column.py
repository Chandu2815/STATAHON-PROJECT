import sqlalchemy
from sqlalchemy import text
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("DATABASE_URL not found in .env file. Exiting.")
    exit()

engine = sqlalchemy.create_engine(DATABASE_URL)

def run_migration():
    """Renames the 'password_hash' column to 'hashed_password'."""
    print("Connecting to the database...")
    try:
        with engine.connect() as connection:
            print("Connection successful.")
            
            inspector = sqlalchemy.inspect(engine)
            columns = inspector.get_columns('users')
            
            has_password_hash = any(c['name'] == 'password_hash' for c in columns)
            has_hashed_password = any(c['name'] == 'hashed_password' for c in columns)

            if has_hashed_password and not has_password_hash:
                print("Column 'hashed_password' already exists and 'password_hash' does not. No migration needed.")
                return

            if not has_password_hash:
                print("Column 'password_hash' not found. Cannot proceed with rename.")
                return

            print("Applying migration: Renaming 'password_hash' to 'hashed_password'...")
            
            with connection.begin():
                connection.execute(text('ALTER TABLE users RENAME COLUMN password_hash TO hashed_password'))

            print("Migration applied successfully!")

    except sqlalchemy.exc.SQLAlchemyError as e:
        print(f"An error occurred during migration: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    run_migration()
