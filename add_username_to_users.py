import sqlalchemy
from sqlalchemy import text
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    print("DATABASE_URL not found in .env file. Exiting.")
    exit()

# For PostgreSQL, the URL should start with 'postgresql'
if not DATABASE_URL.startswith("postgresql"):
    print(f"Database URL '{DATABASE_URL}' is not for PostgreSQL. Exiting.")
    exit()

engine = sqlalchemy.create_engine(DATABASE_URL)

def run_migration():
    """Adds the username column to the users table."""
    print("Connecting to the database...")
    try:
        with engine.connect() as connection:
            print("Connection successful.")
            
            # Check if the column already exists
            inspector = sqlalchemy.inspect(engine)
            columns = inspector.get_columns('users')
            column_exists = any(c['name'] == 'username' for c in columns)

            if column_exists:
                print("Column 'username' already exists in 'users' table.")
                return

            print("Applying migration: Adding 'username' column to 'users' table...")
            
            # Use a transaction to ensure atomicity
            with connection.begin():
                # Add the column. It needs to be nullable temporarily to add it to existing rows.
                connection.execute(text('ALTER TABLE users ADD COLUMN username VARCHAR(100)'))
                
                # Populate the new username column with values from the email column (or another default)
                # This is a placeholder, you might want a different logic
                print("Populating 'username' with email values...")
                connection.execute(text('UPDATE users SET username = email'))

                # Now, make the column NOT NULL if required by your model
                print("Setting 'username' column to NOT NULL...")
                connection.execute(text('ALTER TABLE users ALTER COLUMN username SET NOT NULL'))

                # Add a unique constraint if it's required
                print("Adding UNIQUE constraint to 'username' column...")
                connection.execute(text('ALTER TABLE users ADD CONSTRAINT uq_users_username UNIQUE (username)'))

            print("Migration applied successfully!")

    except sqlalchemy.exc.SQLAlchemyError as e:
        print(f"An error occurred during migration: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    run_migration()
