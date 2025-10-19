import argparse
import json
import psycopg2
import logging
from db import get_db_connection

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def retrieve_results_by_vacancy(vacancy_id):
    """
    Retrieves all results for a given vacancy_id, sorted by score descending.
    Returns a list of dictionaries, where each dictionary represents a result.
    """
    conn, cursor = get_db_connection()
    if not conn:
        logging.error("Failed to connect to the database.")
        return []

    try:
        # Fetch results and order them by score, highest first.
        query = "SELECT * FROM results WHERE vacancy_id = %s ORDER BY score DESC;"
        cursor.execute(query, (vacancy_id,))
        results = cursor.fetchall()

        if not results:
            logging.info(f"No results found for vacancy_id: {vacancy_id}")
            return []

        column_names = [desc[0] for desc in cursor.description]
        processed_results = []

        for row in results:
            record = dict(zip(column_names, row))
            # The 'reasons' column is stored as a JSON string, so we parse it.
            if 'reasons' in record and isinstance(record['reasons'], str):
                try:
                    record['reasons'] = json.loads(record['reasons'])
                except json.JSONDecodeError:
                    logging.warning(f"Could not decode reasons JSON for result ID {record.get('id')}")
            processed_results.append(record)
        return processed_results

    except (psycopg2.Error, json.JSONDecodeError) as e:
        logging.error(f"An error occurred: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Retrieve results for a given vacancy ID.")
    parser.add_argument("vacancy_id", type=int, help="The ID of the vacancy to retrieve results for.")
    args = parser.parse_args()

    print(retrieve_results_by_vacancy(args.vacancy_id))