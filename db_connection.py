import os
import psycopg2
from psycopg2 import Error


def get_connection():
    """Establish and return a connection to the central PostgreSQL database.

    Uses the `DATABASE_URL` environment variable. If the connection fails,
    an exception is raised and no fallback is attempted.
    """
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set in environment")

    try:
        conn = psycopg2.connect(dsn=database_url)
        return conn
    except Error as e:
        # Do not fallback or print instructions that suggest using local DBs.
        raise


if __name__ == "__main__":
    # Test the connection
    try:
        conn = get_connection()
        print("✓ Database connection successful!")
        conn.close()
    except Exception as e:
        print(f"✗ Database connection failed: {e}")
        raise
