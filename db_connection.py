import psycopg2
from psycopg2 import sql, Error


# Database configuration
DB_CONFIG = {
    'host': '187.127.135.117',
    'database': 'survey_db',
    'user': 'survey_user',
    'password': 'StrongPass@123',
    'port': 5432
}


def get_connection():
    """
    Establish and return a connection to the PostgreSQL database.
    
    Returns:
        psycopg2.connection: A database connection object if successful, None otherwise.
    
    Raises:
        Prints error message to console if connection fails.
    """
    try:
        connection = psycopg2.connect(
            host=DB_CONFIG['host'],
            database=DB_CONFIG['database'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            port=DB_CONFIG['port']
        )
        return connection
    except Error as e:
        print(f"Error: Failed to connect to the database.")
        print(f"Details: {e}")
        return None


if __name__ == "__main__":
    # Test the connection
    conn = get_connection()
    if conn:
        print("✓ Database connection successful!")
        conn.close()
    else:
        print("✗ Database connection failed.")
