
from sql_guard import validate_sql


test_queries = [
    "SELECT COUNT(*) FROM hotel_bookings",

    "SELECT hotel, COUNT(*) AS total "
    "FROM hotel_bookings GROUP BY hotel",

    "SELECT * FROM hotel_bookings LIMIT 500",

    "DELETE FROM hotel_bookings",

    "SELECT * FROM users",

    "SELECT * FROM hotel_bookings; DROP TABLE hotel_bookings"
]


for query in test_queries:
    print("\nOriginal query:", query)

    try:
        safe_query = validate_sql(query)
        print("ACCEPTED:", safe_query)

    except ValueError as error:
        print("REJECTED:", error)
