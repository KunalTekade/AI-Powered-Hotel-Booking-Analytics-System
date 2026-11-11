
import os
from pathlib import Path
import mysql.connector
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env", override=True)

connection = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    port=int(os.getenv("MYSQL_PORT", 3306)),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    database=os.getenv("MYSQL_DATABASE")
)

cursor = connection.cursor()

cursor.execute("DESCRIBE hotel_bookings")

columns = cursor.fetchall()

print("\nHOTEL BOOKINGS TABLE SCHEMA\n")

for column in columns:
    print(f"Column: {column[0]} | Type: {column[1]}")

cursor.close()
connection.close()
