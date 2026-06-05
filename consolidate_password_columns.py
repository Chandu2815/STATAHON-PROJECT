import sqlalchemy
from sqlalchemy import text, inspect
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("DATABASE_URL not found in .env file. Exiting.")
    exit()

engine = sqlalchemy.create_engine(DATABASE_URL)

def run_migration():
    """
    Copies data from 'password_hash' to 'hashed_password' if 'hashed_password' is null,
    then drops the 'password_hash' column.
    """
    print("Connecting to the database...")
    try:
        with engine.connect() as connection:
            print("Connection successful.")
            
            inspector = inspect(engine)
            columns = inspector.get_columns('users')
            
            has_password_hash = any(c['name'] == 'password_hash' for c in columns)
            has_hashed_password = any(c['name'] == 'hashed_password' for c in columns)

            if not has_hashed_password:
                print("Column 'hashed_password' does not exist. Cannot proceed.")
                return

            if not has_password_hash:
                print("Column 'password_hash' does not exist. No migration needed.")
                # Ensure hashed_password is not nullable
                with connection.begin():
                    print("Ensuring 'hashed_password' is NOT NULL...")
                    connection.execute(text('ALTER TABLE users ALTER COLUMN hashed_password SET NOT NULL'))
                print("Schema is correct.")
                return

            print("Applying migration: Consolidating password columns...")
            
            with connection.begin():
                # Copy data from password_hash to hashed_password where hashed_password is null
                print("Copying data from 'password_hash' to 'hashed_password' for existing users...")
                connection.execute(text('UPDATE users SET hashed_password = password_hash WHERE hashed_password IS NULL'))

                # Drop the old password_hash column
                print("Dropping legacy 'password_hash' column...")
                connection.execute(text('ALTER TABLE users DROP COLUMN password_hash'))

                # Ensure the new hashed_password column is not nullable
                print("Ensuring 'hashed_password' column is NOT NULL...")
                connection.execute(text('ALTER TABLE users ALTER COLUMN hashed_password SET NOT NULL'))

            print("Migration applied successfully!")

            # Final schema verification
            print("\n--- Final 'users' table schema ---")
            inspector = inspect(engine)
            final_columns = inspector.get_columns('users')
            for col in final_columns:
                print(f"- {col['name']}: {col['type']} (Nullable: {col['nullable']})")


    except sqlalchemy.exc.SQLAlchemyError as e:
        print(f"An error occurred during migration: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    run_migration()
