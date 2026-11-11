
import re

# Allowed database table
ALLOWED_TABLE = "hotel_bookings"


def validate_sql(sql):
    """
    Validates generated SQL before database execution.
    Only SELECT queries are allowed.
    """

    if not sql or not sql.strip():
        return False, "SQL query is empty."

    # Remove markdown SQL formatting
    sql = sql.strip()
    sql = re.sub(r"^```sql\s*", "", sql, flags=re.IGNORECASE)
    sql = re.sub(r"\s*```$", "", sql)

    # Remove trailing semicolon
    sql = sql.rstrip(";").strip()

    # Block multiple statements
    if ";" in sql:
        return False, "Multiple SQL statements are not allowed."

    # Only SELECT queries allowed
    if not re.match(r"^SELECT\b", sql, re.IGNORECASE):
        return False, "Only SELECT queries are allowed."

    # Block dangerous SQL keywords
    blocked_keywords = [
        "INSERT", "UPDATE", "DELETE", "DROP",
        "ALTER", "TRUNCATE", "CREATE", "REPLACE",
        "GRANT", "REVOKE", "EXEC", "EXECUTE"
    ]

    for keyword in blocked_keywords:
        if re.search(rf"\b{keyword}\b", sql, re.IGNORECASE):
            return False, f"Blocked SQL keyword: {keyword}"

    # Allow only the specified table
    tables = re.findall(
        r"\b(?:FROM|JOIN)\s+([a-zA-Z_][a-zA-Z0-9_]*)",
        sql,
        re.IGNORECASE
    )

    if not tables:
        return False, "No database table found."

    if any(table.lower() != ALLOWED_TABLE.lower() for table in tables):
        return False, "Query references an unauthorized table."

    return True, sql


if __name__ == "__main__":

    test_query = """
    SELECT market_segment, COUNT(*) AS total_bookings
    FROM hotel_bookings
    GROUP BY market_segment
    ORDER BY total_bookings DESC
    LIMIT 1;
    """

    is_valid, result = validate_sql(test_query)

    print("\nSQL VALIDATOR TEST")
    print("=" * 50)

    if is_valid:
        print("SQL SAFETY CHECK: PASSED")
        print("VALIDATED SQL:")
        print(result)
    else:
        print("SQL SAFETY CHECK: FAILED")
        print("REASON:", result)
