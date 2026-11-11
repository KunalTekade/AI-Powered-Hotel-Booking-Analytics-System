
import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text, URL

# Load project environment variables
ROOT_DIR = Path(__file__).resolve().parents[1]
load_dotenv(ROOT_DIR / ".env")

# Read-only database credentials
db_url = URL.create(
    drivername="mysql+pymysql",
    username=os.getenv("AI_MYSQL_USER"),
    password=os.getenv("AI_MYSQL_PASSWORD"),
    host="localhost",
    port=3306,
    database=os.getenv("AI_MYSQL_DATABASE")
)

engine = create_engine(db_url)

try:
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT COUNT(*) FROM hotel_bookings")
        )
        count = result.scalar()

        print("Read-only MySQL connection successful!")
        print("Total booking records:", count)

except Exception as error:
    print("Database connection failed:", error)

finally:
    engine.dispose()
