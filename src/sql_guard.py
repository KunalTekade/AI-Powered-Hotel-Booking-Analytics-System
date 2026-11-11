
import sqlglot
from sqlglot import exp


ALLOWED_TABLES = {"hotel_bookings"}
MAX_ROWS = 200


def validate_sql(sql: str) -> str:
    """
    Validate Gemini-generated SQL before database execution.
    Only SELECT queries on hotel_bookings are permitted.
    """

    if not sql or not sql.strip():
        raise ValueError("SQL query is empty.")

    # Parse SQL using MySQL syntax
    try:
        statements = sqlglot.parse(sql, read="mysql")
    except Exception as error:
        raise ValueError(f"Invalid SQL syntax: {error}")

    # Reject multiple statements
    if len(statements) != 1 or statements[0] is None:
        raise ValueError("Only one SQL statement is allowed.")

    query = statements[0]

    # Only SELECT statements are allowed
    if not isinstance(query, exp.Select):
        raise ValueError("Only SELECT queries are allowed.")

    # Reject SELECT INTO and locking clauses
    if query.args.get("into") is not None:
        raise ValueError("SELECT INTO operations are not allowed.")

    if query.args.get("locks"):
        raise ValueError("Locking clauses are not allowed.")

    # Check every referenced table, including nested queries and CTEs
    tables = list(query.find_all(exp.Table))

    if not tables:
        raise ValueError("Query must reference hotel_bookings.")

    for table in tables:
        table_name = table.name.lower()

        if table_name not in ALLOWED_TABLES:
            raise ValueError(
                f"Access denied to table: {table.name}"
            )

        # Reject database-qualified or catalog-qualified references
        if table.db or table.catalog:
            raise ValueError(
                "Database-qualified table references are not allowed."
            )

    # Reject potentially dangerous MySQL functions
    blocked_functions = {
        "SLEEP",
        "BENCHMARK",
        "LOAD_FILE",
        "GET_LOCK",
        "RELEASE_LOCK",
        "IS_FREE_LOCK",
        "IS_USED_LOCK"
    }

    for function in query.find_all(exp.Func):
        function_name = function.sql_name().upper()

        if function_name in blocked_functions:
            raise ValueError(
                f"Restricted SQL function: {function_name}"
            )

        if isinstance(function, exp.Anonymous):
            if function.name.upper() in blocked_functions:
                raise ValueError(
                    f"Restricted SQL function: {function.name}"
                )

    # Enforce a maximum result size
    limit_clause = query.args.get("limit")

    if limit_clause is None:
        query = query.limit(MAX_ROWS)

    else:
        limit_value = limit_clause.expression

        if not isinstance(limit_value, exp.Literal):
            raise ValueError("Only numeric LIMIT values are allowed.")

        if limit_value.is_string:
            raise ValueError("LIMIT must be numeric.")

        try:
            requested_limit = int(limit_value.this)
        except (ValueError, TypeError):
            raise ValueError("Invalid LIMIT value.")

        if requested_limit < 1:
            raise ValueError("LIMIT must be greater than zero.")

        if requested_limit > MAX_ROWS:
            limit_clause.set(
                "expression",
                exp.Literal.number(MAX_ROWS)
            )

    # Return validated MySQL SQL
    return query.sql(dialect="mysql", pretty=True)
