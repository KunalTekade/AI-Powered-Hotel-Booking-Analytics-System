
from gemini_sql import generate_sql
from sql_guard import validate_sql
from query_database import execute_query


def run_analytics(user_question):

    print("\n" + "=" * 60)
    print("HOTEL BOOKING ANALYTICS")
    print("=" * 60)

    try:
        # 1. Generate SQL using Gemini
        print("\n[1] Generating SQL using Gemini...")

        generated_sql = generate_sql(user_question)

        if generated_sql == "UNSUPPORTED":
            print("\nThis question cannot be answered using the database schema.")
            return

        print("\nGENERATED SQL:")
        print(generated_sql)

        # 2. Validate SQL using SQL Guard
        print("\n[2] Validating SQL security...")

        validated_sql = validate_sql(generated_sql)

        print("SQL SAFETY CHECK: PASSED")
        print("\nVALIDATED SQL:")
        print(validated_sql)

        # 3. Execute SQL using MySQL
        print("\n[3] Executing query in MySQL...")

        results = execute_query(validated_sql)

        print("\nDATABASE EXECUTION: SUCCESSFUL")

        # 4. Display actual results
        print("\n" + "=" * 60)
        print("QUERY RESULTS")
        print("=" * 60)

        if not results:
            print("No records found.")
            return

        for index, row in enumerate(results, start=1):
            print(f"\nRecord {index}:")
            for column, value in row.items():
                print(f"{column}: {value}")

        print("\n" + "=" * 60)
        print("ANALYTICS PIPELINE COMPLETED SUCCESSFULLY")
        print("=" * 60)

        return results

    except Exception as error:
        print("\nPIPELINE FAILED")
        print("Error:", error)
        return None


if __name__ == "__main__":

    question = input("\nEnter your question: ").strip()

    if question:
        run_analytics(question)
    else:
        print("Please enter a valid question.")
