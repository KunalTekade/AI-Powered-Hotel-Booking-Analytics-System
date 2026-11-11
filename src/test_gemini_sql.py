
from gemini_sql import generate_sql
from sql_guard import validate_sql

# Questions to test
questions = [
    "What is the total number of bookings?",
    "What is the cancellation rate for each hotel?",
    "Which market segment has the highest number of bookings?"
]

for question in questions:
    print("\n" + "=" * 60)
    print("QUESTION:", question)

    try:
        # Generate SQL using Gemini
        generated_sql = generate_sql(question)

        print("\nGEMINI GENERATED SQL:")
        print(generated_sql)

        # Validate the generated SQL
        if generated_sql == "UNSUPPORTED":
            print("\nRESULT: Question is unsupported.")
            continue

        safe_sql = validate_sql(generated_sql)

        print("\nSQL SAFETY CHECK: PASSED")
        print("VALIDATED SQL:", safe_sql)

    except Exception as error:
        print("\nERROR:", error)
