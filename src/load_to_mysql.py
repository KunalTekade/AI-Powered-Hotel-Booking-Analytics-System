
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
import os

# ==========================================
# 1. LOAD CONFIGURATION
# ==========================================

PROJECT_FOLDER = Path(__file__).resolve().parent.parent

load_dotenv(PROJECT_FOLDER / ".env")

HOST = os.getenv("MYSQL_HOST", "localhost")
PORT = int(os.getenv("MYSQL_PORT", "3306"))
USER = os.getenv("MYSQL_USER", "root")
PASSWORD = os.getenv("MYSQL_PASSWORD")
DATABASE = os.getenv(
    "MYSQL_DATABASE",
    "hotel_booking_analytics"
)

if not PASSWORD:
    raise ValueError(
        "MySQL password missing. Check your .env file."
    )

# ==========================================
# 2. LOAD CLEANED DATA
# ==========================================

DATA_FILE = (
    PROJECT_FOLDER
    / "data"
    / "processed"
    / "hotel_bookings_cleaned.csv"
)

if not DATA_FILE.exists():
    raise FileNotFoundError(
        f"CSV file not found: {DATA_FILE}"
    )

df = pd.read_csv(DATA_FILE)

print("\nMYSQL DATA INTEGRATION")
print("\nCSV loaded successfully.")
print("Dataset shape:", df.shape)

# ==========================================
# 3. CONNECT TO MYSQL SERVER
# ==========================================

connection_url = URL.create(
    drivername="mysql+pymysql",
    username=USER,
    password=PASSWORD,
    host=HOST,
    port=PORT
)

server_engine = create_engine(connection_url)

# ==========================================
# 4. CREATE DATABASE
# ==========================================

with server_engine.connect() as connection:
    connection.execute(
        text(f"CREATE DATABASE IF NOT EXISTS `{DATABASE}`")
    )

print(f"\nDatabase '{DATABASE}' is ready.")

# ==========================================
# 5. CONNECT TO PROJECT DATABASE
# ==========================================

database_url = URL.create(
    drivername="mysql+pymysql",
    username=USER,
    password=PASSWORD,
    host=HOST,
    port=PORT,
    database=DATABASE
)

engine = create_engine(database_url)

# ==========================================
# 6. LOAD DATA INTO MYSQL
# ==========================================

print("\nLoading records into MySQL...")

df.to_sql(
    name="hotel_bookings",
    con=engine,
    if_exists="replace",
    index=False,
    chunksize=1000
)

print("Data loaded successfully!")

# ==========================================
# 7. VERIFY DATA
# ==========================================

with engine.connect() as connection:

    count = connection.execute(
        text("SELECT COUNT(*) FROM hotel_bookings")
    ).scalar()

    columns = connection.execute(
        text("""
            SELECT COUNT(*)
            FROM INFORMATION_SCHEMA.COLUMNS
            WHERE TABLE_SCHEMA = :database
            AND TABLE_NAME = 'hotel_bookings'
        """),
        {"database": DATABASE}
    ).scalar()

print("\nMYSQL VERIFICATION")
print("\nDatabase:", DATABASE)
print("Table: hotel_bookings")
print("Records inserted:", count)
print("Columns inserted:", columns)

if count == len(df) and columns == len(df.columns):
    print("\nSUCCESS: All records transferred!")
    print("\nPHASE 5 STEP 1 COMPLETED!")
else:
    print("\nWARNING: Please verify the transferred data.")

engine.dispose()
server_engine.dispose()
