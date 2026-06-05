import sqlalchemy
from sqlalchemy import inspect
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("DATABASE_URL not found in .env file. Exiting.")
    exit()

engine = sqlalchemy.create_engine(DATABASE_URL)

def inspect_schema():
    """Connects to the database and prints the schema for the 'users' table."""
    print("Connecting to the database to inspect schema...")
    try:
        with engine.connect() as connection:
            print("Connection successful.")
            
            inspector = inspect(engine)
            table_name = 'users'

            if not inspector.has_table(table_name):
                print(f"Table '{table_name}' does not exist.")
                return

            print(f"\n--- Schema for '{table_name}' table ---")
            columns = inspector.get_columns(table_name)
            for col in columns:
                print(
                    f"- Name: {col['name']}, "
                    f"Type: {col['type']}, "
                    f"Nullable: {col['nullable']}, "
                    f"Default: {col['default']}"
                )

    except sqlalchemy.exc.SQLAlchemyError as e:
        print(f"An error occurred during schema inspection: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    inspect_schema()
