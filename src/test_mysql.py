
import os
from pathlib import Path
import mysql.connector
from dotenv import load_dotenv

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=True)

# Connect to MySQL
try:
    connection = mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT", 3306)),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )

    if connection.is_connected():
        print("MySQL connection successful!")

        cursor = connection.cursor()

        # Check database name
        cursor.execute("SELECT DATABASE()")
        print("Connected Database:", cursor.fetchone()[0])

        # Retrieve tables
        cursor.execute("SHOW TABLES")
        tables = cursor.fetchall()

        print("\nAvailable Tables:")

        for table in tables:
            print("-", table[0])

        cursor.close()
        connection.close()

        print("\nMySQL test completed successfully!")

except mysql.connector.Error as error:
    print("MySQL Connection Failed:", error)
