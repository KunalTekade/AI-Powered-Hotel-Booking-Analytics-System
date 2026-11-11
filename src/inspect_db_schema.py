
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, URL

# Load environment variables
ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")

# Connect using the read-only account
db_url = URL.create(
    "mysql+pymysql",
    username=os.getenv("AI_MYSQL_USER"),
    password=os.getenv("AI_MYSQL_PASSWORD"),
    host="localhost",
    port=3306,
    database=os.getenv("AI_MYSQL_DATABASE")
)

engine = create_engine(db_url)

try:
    with engine.connect() as connection:
        columns = connection.execute(
            text("SHOW COLUMNS FROM hotel_bookings")
        )

        print("\nHOTEL_BOOKINGS DATABASE SCHEMA\n")

        for column in columns:
            print(f"{column.Field} : {column.Type}")

except Exception as error:
    print("Error:", error)

finally:
    engine.dispose()
