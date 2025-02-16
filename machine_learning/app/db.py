import psycopg2
import os
from config import Config

def get_db_connection():
    """Establishes and returns a database connection."""
    try:
        conn = psycopg2.connect(os.environ.get('DATABASE_URL'))
        return conn
    except psycopg2.OperationalError as e:
        print(f"Error connecting to the database: {e}")
        return None  # Or raise the exception, depending on your needs

def close_db_connection(conn):
    """Closes the database connection."""
    if conn:
        conn.close()