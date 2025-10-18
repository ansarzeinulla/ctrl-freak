import psycopg2

# --- Your database credentials ---
db_params = {
    "database": "remotedb",
    "user": "remoteuser2",
    "password": "4444",
    "host": "100.100.122.40",
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


# --- Main script execution ---
conn = None  # Initialize conn to None
try:
    # Establish a connection to the database
    conn = psycopg2.connect(**db_params)
    cur = conn.cursor()

    # --- Get Vacancy Details ---
    vacancy_id_input = input("Enter the ID of the VACANCY you want to view: ")
    vacancy_id = int(vacancy_id_input) # Convert input to an integer
    get_record_by_id(cur, "vacancies", vacancy_id)

    # --- Get Resume Details ---
    # IMPORTANT: We are assuming your resumes table is named 'resumes'.
    # If it has a different name, change it in the line below.
    resume_table_name = "resumes" 
    resume_id_input = input(f"\nEnter the ID of the RESUME you want to view (from '{resume_table_name}' table): ")
    resume_id = int(resume_id_input) # Convert input to an integer
    get_record_by_id(cur, resume_table_name, resume_id)


except ValueError:
    print("\nError: Invalid ID. Please enter a number.")
except psycopg2.Error as e:
    print(f"\nDatabase connection error: {e}")
finally:
    # Close the cursor and the connection if they were successfully created
    if 'cur' in locals() and cur:
        cur.close()
    if conn:
        conn.close()
        print("\n\nDatabase connection closed.")