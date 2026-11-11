
-- =====================================================
-- PHASE 6: HOTEL BOOKING BUSINESS ANALYSIS
-- Database: hotel_booking_analytics
-- Table: hotel_bookings
-- MySQL 8.0+
-- =====================================================

USE hotel_booking_analytics;


-- =====================================================
-- 1. BASIC DATA OVERVIEW
-- =====================================================

SELECT
    COUNT(*) AS total_bookings,
    SUM(is_canceled) AS cancelled_bookings,
    SUM(CASE WHEN is_canceled = 0 THEN 1 ELSE 0 END)
        AS non_cancelled_bookings,
    ROUND(AVG(is_canceled) * 100, 2)
        AS cancellation_rate
FROM hotel_bookings;


-- =====================================================
-- 2. BOOKING AND CANCELLATION BY HOTEL
-- =====================================================

SELECT
    hotel,
    COUNT(*) AS total_bookings,
    SUM(is_canceled) AS cancelled_bookings,
    ROUND(AVG(is_canceled) * 100, 2)
        AS cancellation_rate
FROM hotel_bookings
GROUP BY hotel
ORDER BY total_bookings DESC;


-- =====================================================
-- 3. MARKET SEGMENT PERFORMANCE
-- =====================================================

SELECT
    market_segment,
    COUNT(*) AS total_bookings,
    SUM(is_canceled) AS cancelled_bookings,
    ROUND(AVG(is_canceled) * 100, 2)
        AS cancellation_rate
FROM hotel_bookings
GROUP BY market_segment
ORDER BY total_bookings DESC;


-- =====================================================
-- 4. MONTHLY BOOKING TREND
-- =====================================================

SELECT
    DATE_FORMAT(arrival_date, '%Y-%m') AS arrival_month,
    COUNT(*) AS total_bookings,
    SUM(is_canceled) AS cancelled_bookings,
    ROUND(AVG(is_canceled) * 100, 2)
        AS cancellation_rate
FROM hotel_bookings
GROUP BY DATE_FORMAT(arrival_date, '%Y-%m')
ORDER BY arrival_month;


-- =====================================================
-- 5. TOP 10 CUSTOMER COUNTRIES
-- =====================================================

SELECT
    country,
    COUNT(*) AS total_bookings
FROM hotel_bookings
WHERE country IS NOT NULL
  AND country <> 'Unknown'
GROUP BY country
ORDER BY total_bookings DESC
LIMIT 10;


-- =====================================================
-- 6. LEAD TIME ANALYSIS
-- =====================================================

SELECT
    CASE
        WHEN lead_time <= 7 THEN '0-7 days'
        WHEN lead_time <= 30 THEN '8-30 days'
        WHEN lead_time <= 90 THEN '31-90 days'
        WHEN lead_time <= 180 THEN '91-180 days'
        ELSE 'Above 180 days'
    END AS lead_time_group,

    COUNT(*) AS total_bookings,

    ROUND(AVG(is_canceled) * 100, 2)
        AS cancellation_rate

FROM hotel_bookings
GROUP BY lead_time_group
ORDER BY MIN(lead_time);


-- =====================================================
-- 7. CUSTOMER TYPE ANALYSIS
-- =====================================================

SELECT
    customer_type,
    COUNT(*) AS total_bookings,
    ROUND(AVG(is_canceled) * 100, 2)
        AS cancellation_rate,
    ROUND(AVG(adr), 2) AS average_adr
FROM hotel_bookings
GROUP BY customer_type
ORDER BY total_bookings DESC;


-- =====================================================
-- 8. DEPOSIT TYPE AND CANCELLATION
-- =====================================================

SELECT
    deposit_type,
    COUNT(*) AS total_bookings,
    ROUND(AVG(is_canceled) * 100, 2)
        AS cancellation_rate
FROM hotel_bookings
GROUP BY deposit_type
ORDER BY cancellation_rate DESC;


-- =====================================================
-- 9. ROOM TYPE ANALYSIS
-- =====================================================

SELECT
    reserved_room_type,
    assigned_room_type,
    COUNT(*) AS booking_count
FROM hotel_bookings
GROUP BY
    reserved_room_type,
    assigned_room_type
ORDER BY booking_count DESC;


-- =====================================================
-- 10. JOIN: HOTEL PERFORMANCE AND ADR
-- =====================================================

SELECT
    h.hotel,
    h.total_bookings,
    h.cancellation_rate,
    a.average_adr
FROM
(
    SELECT
        hotel,
        COUNT(*) AS total_bookings,
        ROUND(AVG(is_canceled) * 100, 2)
            AS cancellation_rate
    FROM hotel_bookings
    GROUP BY hotel
) AS h

JOIN
(
    SELECT
        hotel,
        ROUND(AVG(adr), 2) AS average_adr
    FROM hotel_bookings
    GROUP BY hotel
) AS a
ON h.hotel = a.hotel;


-- =====================================================
-- 11. CTE: ESTIMATED ROOM VALUE BY HOTEL
-- =====================================================

WITH hotel_revenue AS
(
    SELECT
        hotel,
        COUNT(*) AS non_cancelled_bookings,

        SUM(
            CASE
                WHEN adr >= 0 AND total_nights > 0
                THEN adr * total_nights
                ELSE 0
            END
        ) AS estimated_room_value

    FROM hotel_bookings
    WHERE is_canceled = 0
    GROUP BY hotel
)

SELECT
    hotel,
    non_cancelled_bookings,
    ROUND(estimated_room_value, 2)
        AS estimated_room_value

FROM hotel_revenue
ORDER BY estimated_room_value DESC;


-- =====================================================
-- 12. WINDOW FUNCTION: RANK HOTELS BY CANCELLATION
-- =====================================================

WITH hotel_cancellation AS
(
    SELECT
        hotel,
        ROUND(AVG(is_canceled) * 100, 2)
            AS cancellation_rate
    FROM hotel_bookings
    GROUP BY hotel
)

SELECT
    hotel,
    cancellation_rate,

    RANK() OVER (
        ORDER BY cancellation_rate DESC
    ) AS cancellation_rank

FROM hotel_cancellation;


-- =====================================================
-- 13. WINDOW FUNCTION: MONTH-OVER-MONTH CHANGE
-- =====================================================

WITH monthly_data AS
(
    SELECT
        DATE_FORMAT(arrival_date, '%Y-%m')
            AS arrival_month,

        COUNT(*) AS total_bookings

    FROM hotel_bookings
    GROUP BY DATE_FORMAT(arrival_date, '%Y-%m')
),

monthly_comparison AS
(
    SELECT
        arrival_month,
        total_bookings,

        LAG(total_bookings) OVER (
            ORDER BY arrival_month
        ) AS previous_month_bookings

    FROM monthly_data
)

SELECT
    arrival_month,
    total_bookings,
    previous_month_bookings,

    total_bookings - previous_month_bookings
        AS booking_difference,

    ROUND(
        (total_bookings - previous_month_bookings)
        * 100.0
        / NULLIF(previous_month_bookings, 0),
        2
    ) AS month_over_month_change_percent

FROM monthly_comparison
ORDER BY arrival_month;


-- =====================================================
-- 14. WINDOW FUNCTION: RANK TOP COUNTRIES
-- =====================================================

WITH country_bookings AS
(
    SELECT
        country,
        COUNT(*) AS total_bookings
    FROM hotel_bookings
    WHERE country IS NOT NULL
      AND country <> 'Unknown'
    GROUP BY country
)

SELECT
    country,
    total_bookings,

    DENSE_RANK() OVER (
        ORDER BY total_bookings DESC
    ) AS country_rank

FROM country_bookings
ORDER BY country_rank
LIMIT 10;


-- =====================================================
-- END OF PHASE 6 SQL ANALYSIS



