
import os
import re
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai import errors


# =====================================================
# 1. LOAD ENVIRONMENT VARIABLES
# =====================================================

ROOT_DIR = Path(__file__).resolve().parents[1]

load_dotenv(ROOT_DIR / ".env", override=True)

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("Gemini API key not found in .env file.")


# =====================================================
# 2. INITIALIZE GEMINI CLIENT
# =====================================================

client = genai.Client(api_key=API_KEY)

MODEL_NAME = "gemini-3.5-flash"


# =====================================================
# 3. DATABASE SCHEMA
# =====================================================

DATABASE_SCHEMA = """
Database: hotel_booking_analytics

Table: hotel_bookings

Columns:

booking_id TEXT
hotel TEXT
is_canceled BIGINT
lead_time BIGINT
arrival_date_year BIGINT
arrival_date_month TEXT
arrival_date_week_number BIGINT
arrival_date_day_of_month BIGINT
stays_in_weekend_nights BIGINT
stays_in_week_nights BIGINT
adults BIGINT
children BIGINT
babies BIGINT
meal TEXT
country TEXT
market_segment TEXT
distribution_channel TEXT
is_repeated_guest BIGINT
previous_cancellations BIGINT
previous_bookings_not_canceled BIGINT
reserved_room_type TEXT
assigned_room_type TEXT
booking_changes BIGINT
deposit_type TEXT
agent DOUBLE
company DOUBLE
days_in_waiting_list BIGINT
customer_type TEXT
adr DOUBLE
required_car_parking_spaces BIGINT
total_of_special_requests BIGINT
reservation_status TEXT
reservation_status_date TEXT
has_agent BIGINT
has_company BIGINT
arrival_date TEXT
total_guests BIGINT
total_nights BIGINT
estimated_revenue DOUBLE
arrival_month_number BIGINT
arrival_year BIGINT
"""


# =====================================================
# 4. GEMINI PROMPT
# =====================================================

def build_prompt(user_question):

    prompt = f"""
You are an expert MySQL data analyst.

Your task is to convert natural language questions
into accurate MySQL SELECT queries.

DATABASE SCHEMA:
{DATABASE_SCHEMA}


IMPORTANT DATA DEFINITIONS:

1. is_canceled = 1 means cancelled.
2. is_canceled = 0 means not cancelled.
3. hotel contains hotel categories such as
   City Hotel and Resort Hotel.
4. estimated_revenue is an estimated booking value,
   NOT verified cash revenue.
5. arrival_month_number is the numeric arrival month.
6. arrival_year is the numeric arrival year.
7. total_guests is the total number of guests.
8. total_nights is the total number of nights.
9. has_agent indicates whether an agent is associated.
10. has_company indicates whether a company is associated.


SQL GENERATION RULES:

1. Generate only MySQL SELECT queries.
2. Use only the hotel_bookings table.
3. Use only columns listed in the schema.
4. Never generate INSERT, UPDATE, DELETE, DROP,
   ALTER, CREATE, TRUNCATE or other modification queries.
5. Never access another table or database.
6. Never generate multiple SQL statements.
7. Use a reasonable LIMIT of at most 200 rows
   for detail-level results.
8. For aggregate queries, use appropriate GROUP BY.
9. Do not invent data or column names.
10. Use valid MySQL syntax.
11. Return SQL only, without Markdown code fences
    or explanations.
12. If the question cannot be answered using this
    schema, return exactly: UNSUPPORTED.
13. When calculating cancellation rates, use
    AVG(is_canceled) * 100 and label the result
    cancellation_rate_percent.
14. For booking counts, use COUNT(*).
15. Do not assume estimated_revenue represents
    actual collected payments.


USER QUESTION:
{user_question}


RETURN:
Only the SQL query or UNSUPPORTED.
"""

    return prompt


# =====================================================
# 5. CLEAN GEMINI RESPONSE
# =====================================================

def clean_sql(sql):

    if not sql:
        raise ValueError("Gemini returned an empty response.")

    sql = sql.strip()

    # Remove Markdown code fences
    sql = re.sub(
        r"^```(?:sql)?\s*",
        "",
        sql,
        flags=re.IGNORECASE
    )

    sql = re.sub(
        r"\s*```$",
        "",
        sql
    )

    return sql.strip()


# =====================================================
# 6. GENERATE SQL USING GEMINI
# =====================================================

def generate_sql(user_question: str) -> str:

    if not user_question or not user_question.strip():
        raise ValueError("Please enter a valid question.")

    prompt = build_prompt(user_question)

    max_attempts = 3

    for attempt in range(max_attempts):

        try:

            print(
                f"\nConnecting to Gemini "
                f"(Attempt {attempt + 1}/{max_attempts})..."
            )

            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt
            )

            if not response or not response.text:
                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            sql = clean_sql(response.text)

            if sql.upper().rstrip(";").strip() == "UNSUPPORTED":
                return "UNSUPPORTED"

            return sql

        except errors.APIError as error:

            status_code = getattr(error, "code", None)

            # Retry temporary server or rate-limit errors
            retryable_codes = (429, 500, 502, 503, 504)

            if status_code not in retryable_codes:
                raise

            if attempt == max_attempts - 1:
                print("\nGemini service is currently unavailable.")
                raise

            wait_time = 2 ** (attempt + 1)

            print(
                f"\nGemini temporarily unavailable "
                f"(HTTP {status_code})."
            )

            print(f"Retrying in {wait_time} seconds...")

            time.sleep(wait_time)

    raise RuntimeError("Unable to generate SQL.")


# =====================================================
# 7. TERMINAL TESTING
# =====================================================

if __name__ == "__main__":

    print("=" * 55)
    print("       HOTEL BOOKING ANALYTICS - GEMINI SQL")
    print("=" * 55)

    question = input("\nEnter your question: ").strip()

    try:

        print("\nGenerating SQL using Gemini...")

        sql_query = generate_sql(question)

        print("\n" + "=" * 55)
        print("GENERATED SQL")
        print("=" * 55)

        print(sql_query)

        print("\n" + "=" * 55)
        print("SQL GENERATION COMPLETED")
        print("=" * 55)

    except Exception as error:

        print("\nSQL GENERATION FAILED")
        print("Error:", error)
