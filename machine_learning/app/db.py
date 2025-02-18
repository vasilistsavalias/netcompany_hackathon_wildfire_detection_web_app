import psycopg2
from psycopg2 import pool
import os
from flask import current_app

# Global variable to hold the connection pool
db_pool = None

def get_db_connection():
    """Gets a connection from the connection pool."""
    global db_pool
    try:
        if db_pool is None:
            # Use os.environ.get() for DATABASE_URL, with a fallback for local development
            db_url = os.environ.get('DATABASE_URL')
            if db_url is None:
                current_app.logger.warning("DATABASE_URL not set, using default SQLite for local development.")
                db_url = "sqlite:///app.db" # Fallback for local testing
            db_pool = psycopg2.pool.SimpleConnectionPool(1, 20, db_url)  # Adjust min/max connections
        return db_pool.getconn()
    except psycopg2.DatabaseError as e:
        current_app.logger.error(f"Database connection error: {e}")
        return None
    except Exception as e:
        current_app.logger.error(f"Unexpected error: {e}")
        return None


def close_db_connection(conn):
    """Returns a connection to the connection pool."""
    global db_pool
    if db_pool and conn:
        db_pool.putconn(conn)

def close_all_connections():
    """Closes all connections in the pool (useful for testing/cleanup)."""
    global db_pool
    if db_pool:
        db_pool.closeall()