
from src.gemini_sql import generate_sql
from src.sql_guard import validate_sql
from src.query_database import execute_query
from src.result_explainer import explain_results


def ask_database(user_question: str):

    try:
        # Step 1: Generate SQL
        generated_sql = generate_sql(user_question)

        print("\nGenerated SQL:")
        print(generated_sql)

        # Step 2: Validate SQL
        validated_sql = validate_sql(generated_sql)

        print("\nSQL Safety Check: PASSED")
        print("Validated SQL:")
        print(validated_sql)

        # Step 3: Execute SQL
        results = execute_query(validated_sql)

        print("\nDatabase Execution: SUCCESS")
        print("Query Results:", results)

        # Step 4: Generate natural-language explanation
        answer = explain_results(user_question, results)

        print("\nAI Explanation Generated: SUCCESS")

        return {
            "success": True,
            "question": user_question,
            "generated_sql": generated_sql,
            "validated_sql": validated_sql,
            "results": results,
            "answer": answer,
            "error": None
        }

    except Exception as error:

        return {
            "success": False,
            "question": user_question,
            "generated_sql": None,
            "validated_sql": None,
            "results": None,
            "answer": None,
            "error": str(error)
        }


if __name__ == "__main__":

    question = "Which market segment has the highest number of bookings?"

    response = ask_database(question)

    print("\n========== FINAL AI ANALYST RESPONSE ==========")

    if response["success"]:
        print("Question:", response["question"])
        print("Answer:", response["answer"])
    else:
        print("Error:", response["error"])
