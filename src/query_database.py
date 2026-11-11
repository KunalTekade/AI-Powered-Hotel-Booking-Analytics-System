
import os
import mysql.connector
from dotenv import load_dotenv

# Load environment variables from project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
load_dotenv(os.path.join(BASE_DIR, ".env"))


def execute_query(sql: str):
    """
    Execute a previously validated, read-only SQL query
    against the MySQL database.

    Returns:
        list: Query results as dictionaries.
    """

    if not sql or not sql.strip():
        raise ValueError("SQL query cannot be empty.")

    connection = None
    cursor = None

    try:
        # Connect using the dedicated MySQL read-only account
        connection = mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            port=int(os.getenv("MYSQL_PORT", 3306)),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE"),
            connection_timeout=10
        )

        if not connection.is_connected():
            raise ConnectionError("Unable to connect to MySQL.")

        # Start a read-only transaction
        connection.start_transaction(readonly=True)

        cursor = connection.cursor(dictionary=True)

        # Execute SQL that has already passed sql_guard.py
        cursor.execute(sql)

        # Return results as a list of dictionaries
        if cursor.description is None:
            raise ValueError("The SQL query did not return a result set.")

        results = cursor.fetchall()

        return results

    except mysql.connector.Error as error:
        raise RuntimeError(
            f"MySQL execution error: {error}"
        ) from error

    finally:
        if cursor is not None:
            cursor.close()

        if connection is not None and connection.is_connected():
            connection.rollback()
            connection.close()
