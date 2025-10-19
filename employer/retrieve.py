import argparse
import json
import psycopg2
import logging
from db import get_db_connection

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def retrieve_results_by_vacancy(vacancy_id):
    """
    Retrieves all results for a given vacancy_id and prints them.
    The 'output' column, which is a JSON string, is parsed and pretty-printed
    with Cyrillic characters displayed correctly.
    """
    conn, cursor = get_db_connection()
    if not conn:
        return "Failed to connect to the database."

    try:
        query = "SELECT * FROM results WHERE vacancy_id = %s;"
        cursor.execute(query, (vacancy_id,))
        results = cursor.fetchall()

        if not results:
            return f"No results found for vacancy_id: {vacancy_id}"

        column_names = [desc[0] for desc in cursor.description]
        output_string = f"--- Found {len(results)} result(s) for Vacancy ID: {vacancy_id} ---\n"

        for i, row in enumerate(results):
            output_string += f"\n--- Result {i+1} ---\n"
            record = dict(zip(column_names, row))
            for key, value in record.items():
                if key == 'output' and isinstance(value, str):
                    # Parse the JSON string and then dump it back to a string
                    # with nice formatting and ensuring Cyrillic is not escaped.
                    # The data might be double-encoded (a JSON string inside a JSON string),
                    # so we parse it, and if the result is still a string, we parse it again.
                    data = json.loads(value)
                    if isinstance(data, str):
                        data = json.loads(data) # Second parse

                    pretty_output = json.dumps(data, indent=2, ensure_ascii=False)
                    output_string += f"{key.ljust(20)}: {pretty_output}\n"
                else:
                    output_string += f"{key.ljust(20)}: {value}\n"
        return output_string

    except (psycopg2.Error, json.JSONDecodeError) as e:
        logging.error(f"An error occurred: {e}")
        return f"An error occurred while retrieving results: {e}"
    finally:
        cursor.close()
        conn.close()
        logging.info("Database connection closed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retrieve results for a given vacancy ID.")
    parser.add_argument("vacancy_id", type=int, help="The ID of the vacancy to retrieve results for.")
    args = parser.parse_args()

    print(retrieve_results_by_vacancy(args.vacancy_id))