import psycopg2
from psycopg2.extras import Json
import os
import json
import logging

# --- Your database credentials ---
# Use host.docker.internal if running in docker, otherwise localhost
db_params = {
    "database": "remotedb",
    "user": "postgres",
    "password": "",
    "host": os.environ.get("DOCKER_DB_HOST", "127.0.0.1"),
    "port": "5432"
}

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_record_by_id(cursor, table_name, record_id):
    """
    Fetches and displays a single record from a specified table by its ID.
    """
    try:
        # Securely create the query with a placeholder for the ID
        query = f"SELECT * FROM {table_name} WHERE id = %s;"
        
        # Execute the query, passing the ID as a parameter to prevent SQL injection
        cursor.execute(query, (record_id,))
        
        # Fetch exactly one record
        record = cursor.fetchone()

        if record:
            print(f"\n--- Details for {table_name.capitalize()} with ID: {record_id} ---")
            column_names = [desc[0] for desc in cursor.description]
            
            # Print data in a readable key-value format
            for col_name, value in zip(column_names, record):
                print(f"{col_name.ljust(20)}: {value}")
        else:
            print(f"\nNo record found in table '{table_name}' with ID: {record_id}")
            
    except psycopg2.Error as e:
        # Handle potential errors like the table not existing
        print(f"An error occurred while fetching from '{table_name}': {e}")
        # It's good practice to roll back in case of an error
        cursor.connection.rollback()

def fetch_record_as_dict(cursor, table_name, record_id):
    """
    Fetches a single record by ID and returns it as a dictionary.
    """
    try:
        query = f"SELECT * FROM {table_name} WHERE id = %s;"
        cursor.execute(query, (record_id,))
        record = cursor.fetchone()

        if not record:
            return None

        column_names = [desc[0] for desc in cursor.description]
        return dict(zip(column_names, record))

    except psycopg2.Error as e:
        print(f"An error occurred while fetching from '{table_name}': {e}")
        # It's good practice to roll back in case of an error
        cursor.connection.rollback()
        return None

def insert_or_update_result(cursor, vacancy_id, resume_id, output):
    """
    Inserts a new result into the 'results' table.
    If a result with the same vacancy_id and resume_id already exists,
    it updates the output. This requires a UNIQUE constraint on (vacancy_id, resume_id).
    """
    try:
        logging.info(f"Attempting to insert/update result for vacancy_id: {vacancy_id}, resume_id: {resume_id}")
        # Serialize the output dictionary into a JSON-formatted string.
        # This string will be stored in a TEXT column in the database.
        string_output = json.dumps(output, ensure_ascii=False)
        # UPSERT query: Insert or update on conflict
        query = """
            INSERT INTO results (vacancy_id, resume_id, output)
            VALUES (%s, %s, %s)
            ON CONFLICT (vacancy_id, resume_id)
            DO UPDATE SET output = EXCLUDED.output;
        """
        
        cursor.execute(query, (vacancy_id, resume_id, string_output))
        cursor.connection.commit()
        logging.info(f"Successfully saved result for vacancy_id: {vacancy_id}, resume_id: {resume_id}")

    except psycopg2.Error as e:
        logging.error(f"An error occurred while saving the result: {e}")
        cursor.connection.rollback()

def get_db_connection():
    """Establishes and returns a database connection and cursor."""
    try:
        logging.info(f"Connecting to database with params: {db_params}")
        # Connect and explicitly set the client encoding to UTF-8
        conn = psycopg2.connect(**db_params, client_encoding='UTF8')
        # conn.set_client_encoding('UTF8') # This is an alternative way to do it
        logging.info("Database connection successful.")
        return conn, conn.cursor()
    except psycopg2.OperationalError as e:
        logging.error(f"Could not connect to the database: {e}")
        logging.error("If running in Docker, ensure DOCKER_DB_HOST is set correctly in your docker-compose file (e.g., to your DB service name).")
        return None, None