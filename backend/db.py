import psycopg2

# --- Your database credentials ---
db_params = {
    "database": "remotedb",
    "user": "postgres",
    "password": "",
    "host": "127.0.0.1",
    "port": "5432"
}

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

def get_db_connection():
    """Establishes and returns a database connection and cursor."""
    conn = psycopg2.connect(**db_params)
    return conn, conn.cursor()