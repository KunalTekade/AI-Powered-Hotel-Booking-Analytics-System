
import os
import sys
from pathlib import Path

import pandas as pd
import streamlit as st
import plotly.express as px

from sqlalchemy import create_engine, URL
from dotenv import load_dotenv


# ==================================================
# 1. PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Booking Analytics | Intelligence Platform",
    page_icon="📊",
    layout="wide"
)


# ==================================================
# 2. PROJECT PATHS AND ENVIRONMENT
# ==================================================

CURRENT_DIR = Path(__file__).resolve().parent

# Automatically locate the project root containing src/ai_analyst.py
ROOT_DIR = next(
    (
        path for path in [CURRENT_DIR, *CURRENT_DIR.parents]
        if (path / "src" / "ai_analyst.py").exists()
    ),
    CURRENT_DIR
)

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

load_dotenv(ROOT_DIR / ".env")


# ==================================================
# 3. AI ANALYST IMPORT
# ==================================================

try:
    from src.ai_analyst import ask_database
    AI_IMPORT_ERROR = None

except Exception as error:
    ask_database = None
    AI_IMPORT_ERROR = str(error)


# ==================================================
# 4. DATABASE CONNECTION
# ==================================================

@st.cache_resource
def get_engine():

    required = [
        "MYSQL_HOST",
        "MYSQL_USER",
        "MYSQL_PASSWORD",
        "MYSQL_DATABASE"
    ]

    missing = [
        key for key in required
        if not os.getenv(key)
    ]

    if missing:
        raise ValueError(
            "Missing database settings in .env: "
            + ", ".join(missing)
        )

    connection_url = URL.create(
        drivername="mysql+pymysql",
        username=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        host=os.getenv("MYSQL_HOST"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        database=os.getenv("MYSQL_DATABASE")
    )

    return create_engine(
        connection_url,
        pool_pre_ping=True
    )


# ==================================================
# 5. LOAD DATA FROM MYSQL
# ==================================================

@st.cache_data(ttl=600)
def load_data():

    engine = get_engine()

    query = "SELECT * FROM hotel_bookings"

    with engine.connect() as connection:
        df = pd.read_sql_query(query, connection)

    return df


# ==================================================
# 6. DASHBOARD HEADER
# ==================================================

st.title("📊 Booking Analytics & Intelligence Platform")

st.caption(
    "Interactive Business Intelligence Dashboard "
    "| Python • MySQL • Streamlit • Plotly • Gemini AI"
)


# ==================================================
# 7. LOAD AND PREPARE DATA
# ==================================================

try:

    df = load_data()

except Exception as error:

    st.error(
        "Unable to connect to MySQL or load the dataset."
    )

    st.info(
        "Check your .env credentials, MySQL service, "
        "database name and hotel_bookings table."
    )

    with st.expander("Technical Details"):
        st.code(str(error))

    st.stop()


required_columns = [
    "hotel",
    "is_canceled",
    "arrival_date",
    "market_segment",
    "customer_type",
    "country",
    "adr",
    "lead_time",
    "total_nights",
    "total_guests"
]

missing_columns = [
    column for column in required_columns
    if column not in df.columns
]

if missing_columns:

    st.error(
        f"Missing database columns: {missing_columns}"
    )

    st.stop()


df["arrival_date"] = pd.to_datetime(
    df["arrival_date"],
    errors="coerce"
)

numeric_columns = [
    "adr",
    "lead_time",
    "total_nights",
    "total_guests",
    "is_canceled"
]

for column in numeric_columns:

    df[column] = pd.to_numeric(
        df[column],
        errors="coerce"
    )

df["arrival_year"] = df["arrival_date"].dt.year

df["booking_status"] = df["is_canceled"].map({
    0: "Not Cancelled",
    1: "Cancelled"
})


# ==================================================
# 8. SIDEBAR FILTERS
# ==================================================

st.sidebar.title("🎛️ Dashboard Controls")

st.sidebar.markdown(
    "Filter the hotel booking dataset"
)

years = sorted(
    df["arrival_year"].dropna().unique().tolist()
)

hotels = sorted(
    df["hotel"].dropna().unique().tolist()
)

segments = sorted(
    df["market_segment"].dropna().unique().tolist()
)

customer_types = sorted(
    df["customer_type"].dropna().unique().tolist()
)

selected_years = st.sidebar.multiselect(
    "Arrival Year",
    years,
    default=years
)

selected_hotels = st.sidebar.multiselect(
    "Hotel",
    hotels,
    default=hotels
)

selected_segments = st.sidebar.multiselect(
    "Market Segment",
    segments,
    default=segments
)

selected_customers = st.sidebar.multiselect(
    "Customer Type",
    customer_types,
    default=customer_types
)

if st.sidebar.button(
    "🔄 Refresh Dashboard",
    use_container_width=True
):

    st.cache_data.clear()
    st.rerun()


# ==================================================
# 9. FILTER DATA
# ==================================================

filtered_df = df[
    df["arrival_year"].isin(selected_years)
    & df["hotel"].isin(selected_hotels)
    & df["market_segment"].isin(selected_segments)
    & df["customer_type"].isin(selected_customers)
].copy()


has_filtered_data = not filtered_df.empty

if not has_filtered_data:

    st.warning(
        "No records found for the selected filters. "
        "Change your filters to view business analytics. "
        "The AI Analyst below can still query the full database."
    )


# ==================================================
# 10. BUSINESS PERFORMANCE OVERVIEW
# ==================================================

st.markdown("## 📌 Business Performance Overview")

if has_filtered_data:

    total_bookings = len(filtered_df)

    cancelled_bookings = int(
        (filtered_df["is_canceled"] == 1).sum()
    )

    active_bookings = int(
        (filtered_df["is_canceled"] == 0).sum()
    )

    cancellation_rate = (
        cancelled_bookings / total_bookings * 100
        if total_bookings else 0
    )

    average_adr = filtered_df.loc[
        filtered_df["adr"] >= 0,
        "adr"
    ].mean()

    average_lead_time = filtered_df[
        "lead_time"
    ].mean()

    total_guests = filtered_df[
        "total_guests"
    ].sum()

    revenue_data = filtered_df[
        (filtered_df["is_canceled"] == 0)
        & (filtered_df["adr"] >= 0)
        & (filtered_df["total_nights"] > 0)
    ]

    estimated_room_value = (
        revenue_data["adr"]
        * revenue_data["total_nights"]
    ).sum()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Total Bookings",
        f"{total_bookings:,}"
    )

    col2.metric(
        "Cancelled Bookings",
        f"{cancelled_bookings:,}"
    )

    col3.metric(
        "Cancellation Rate",
        f"{cancellation_rate:.2f}%"
    )

    col4.metric(
        "Average ADR",
        f"€{average_adr:,.2f}"
        if pd.notna(average_adr)
        else "N/A"
    )

    col5, col6, col7, col8 = st.columns(4)

    col5.metric(
        "Active Bookings",
        f"{active_bookings:,}"
    )

    col6.metric(
        "Total Guests",
        f"{total_guests:,.0f}"
    )

    col7.metric(
        "Average Lead Time",
        f"{average_lead_time:.1f} days"
        if pd.notna(average_lead_time)
        else "N/A"
    )

    col8.metric(
        "Estimated Room Value",
        f"€{estimated_room_value:,.0f}"
    )

    st.caption(
        "Estimated room value is calculated using "
        "non-cancelled bookings: ADR × total nights. "
        "It is not verified cash revenue."
    )

else:

    st.info(
        "Business KPIs are unavailable because "
        "the selected filters returned no records."
    )

st.divider()


# ==================================================
# 11. MONTHLY BOOKING TREND
# ==================================================

st.markdown("## 📈 Booking Trends")

if has_filtered_data:

    monthly_data = filtered_df.dropna(
        subset=["arrival_date"]
    ).copy()

    monthly_data["month"] = (
        monthly_data["arrival_date"]
        .dt.to_period("M")
        .astype(str)
    )

    monthly_summary = (
        monthly_data.groupby("month")
        .agg(
            total_bookings=("is_canceled", "count"),
            cancelled=("is_canceled", "sum")
        )
        .reset_index()
    )

    monthly_summary["not_cancelled"] = (
        monthly_summary["total_bookings"]
        - monthly_summary["cancelled"]
    )

    fig_monthly = px.line(
        monthly_summary,
        x="month",
        y="total_bookings",
        markers=True,
        title="Monthly Booking Trend",
        labels={
            "month": "Month",
            "total_bookings": "Number of Bookings"
        }
    )

    fig_monthly.update_layout(
        xaxis_tickangle=-45,
        hovermode="x unified"
    )

    st.plotly_chart(
        fig_monthly,
        use_container_width=True
    )

else:

    st.info("Monthly booking trend is unavailable.")


# ==================================================
# 12. HOTEL PERFORMANCE ANALYSIS
# ==================================================

st.markdown("## 🏨 Hotel Performance Analysis")

if has_filtered_data:

    col1, col2 = st.columns(2)

    hotel_summary = (
        filtered_df.groupby("hotel")
        .agg(
            total_bookings=("is_canceled", "count"),
            cancellation_rate=("is_canceled", "mean")
        )
        .reset_index()
    )

    hotel_summary["cancellation_rate"] *= 100

    with col1:

        fig_hotel = px.bar(
            hotel_summary,
            x="hotel",
            y="total_bookings",
            color="hotel",
            title="Bookings by Hotel",
            text_auto=True
        )

        st.plotly_chart(
            fig_hotel,
            use_container_width=True
        )

    with col2:

        fig_cancel = px.bar(
            hotel_summary,
            x="hotel",
            y="cancellation_rate",
            color="hotel",
            title="Cancellation Rate by Hotel",
            text_auto=".2f"
        )

        fig_cancel.update_layout(
            yaxis_title="Cancellation Rate (%)"
        )

        st.plotly_chart(
            fig_cancel,
            use_container_width=True
        )

else:

    st.info("Hotel performance data is unavailable.")


# ==================================================
# 13. CUSTOMER AND MARKET ANALYSIS
# ==================================================

st.markdown("## 👥 Customer & Market Analysis")

if has_filtered_data:

    col1, col2 = st.columns(2)

    segment_summary = (
        filtered_df.groupby("market_segment")
        .agg(
            bookings=("is_canceled", "count"),
            cancellation_rate=("is_canceled", "mean")
        )
        .reset_index()
    )

    segment_summary["cancellation_rate"] *= 100

    with col1:

        fig_segment = px.bar(
            segment_summary.sort_values(
                "bookings",
                ascending=False
            ),
            x="market_segment",
            y="bookings",
            title="Bookings by Market Segment",
            color="market_segment",
            text_auto=True
        )

        fig_segment.update_layout(
            xaxis_tickangle=-35
        )

        st.plotly_chart(
            fig_segment,
            use_container_width=True
        )

    with col2:

        fig_customer = px.pie(
            filtered_df,
            names="customer_type",
            title="Customer Type Distribution",
            hole=0.45
        )

        st.plotly_chart(
            fig_customer,
            use_container_width=True
        )

else:

    st.info("Customer and market data is unavailable.")


# ==================================================
# 14. GEOGRAPHICAL ANALYSIS
# ==================================================

st.markdown("## 🌍 Customer Geography")

if has_filtered_data:

    country_summary = (
        filtered_df["country"]
        .fillna("Unknown")
        .value_counts()
        .head(10)
        .rename_axis("country")
        .reset_index(name="bookings")
    )

    fig_country = px.bar(
        country_summary.sort_values("bookings"),
        x="bookings",
        y="country",
        orientation="h",
        title="Top 10 Countries by Booking Count",
        text_auto=True
    )

    st.plotly_chart(
        fig_country,
        use_container_width=True
    )

else:

    st.info("Geographical data is unavailable.")


# ==================================================
# 15. BOOKING BEHAVIOUR ANALYSIS
# ==================================================

st.markdown("## 🔍 Booking Behaviour Analysis")

if has_filtered_data:

    col1, col2 = st.columns(2)

    with col1:

        lead_data = filtered_df[
            filtered_df["lead_time"].notna()
            & (filtered_df["lead_time"] >= 0)
        ]

        if not lead_data.empty:

            fig_lead = px.box(
                lead_data,
                x="booking_status",
                y="lead_time",
                color="booking_status",
                title="Lead Time vs Booking Status"
            )

            st.plotly_chart(
                fig_lead,
                use_container_width=True
            )

        else:

            st.info("No valid lead-time data.")

    with col2:

        adr_data = filtered_df[
            filtered_df["adr"].notna()
            & (filtered_df["adr"] >= 0)
        ]

        if not adr_data.empty:

            fig_adr = px.box(
                adr_data,
                x="hotel",
                y="adr",
                color="hotel",
                title="ADR Distribution by Hotel"
            )

            st.plotly_chart(
                fig_adr,
                use_container_width=True
            )

        else:

            st.info("No valid ADR data.")

else:

    st.info("Booking behaviour data is unavailable.")


# ==================================================
# 16. DATA EXPLORER
# ==================================================

st.divider()

st.markdown("## 🗂️ Booking Data Explorer")

if has_filtered_data:

    st.write(
        "Explore the filtered booking records and "
        "download them for further analysis."
    )

    st.dataframe(
        filtered_df.head(1000),
        use_container_width=True,
        hide_index=True
    )

    csv_data = filtered_df.to_csv(
        index=False
    ).encode("utf-8")

    st.download_button(
        label="⬇️ Download Filtered Data (CSV)",
        data=csv_data,
        file_name="booking_analytics_filtered.csv",
        mime="text/csv"
    )

else:

    st.info("No filtered records available to explore.")


# ==================================================
# 17. AI-POWERED NATURAL LANGUAGE ANALYTICS
# ==================================================

st.divider()

st.title("🧠 AI-Powered Data Analyst")

st.caption(
    "Natural Language to SQL | Gemini AI | "
    "SQL Guard | MySQL | Business Intelligence"
)

st.markdown(
    "Ask questions about hotel booking data in natural language. "
    "Gemini generates SQL, SQL Guard validates it, "
    "and MySQL returns actual database results."
)


# ==================================================
# 18. SUGGESTED QUESTIONS
# ==================================================

st.markdown("### 💡 Suggested Questions")

sample_questions = [
    "Which market segment has the highest number of bookings?",
    "Which country has the most bookings?",
    "What is the overall cancellation rate?",
    "Which hotel has the highest average ADR?"
]

col1, col2 = st.columns(2)

with col1:

    st.info(sample_questions[0])
    st.info(sample_questions[1])

with col2:

    st.info(sample_questions[2])
    st.info(sample_questions[3])


# ==================================================
# 19. SESSION STATE
# ==================================================

if "ai_question_history" not in st.session_state:

    st.session_state.ai_question_history = []


# ==================================================
# 20. AUTOMATIC CHART GENERATION
# ==================================================

def create_ai_chart(result_df):

    if result_df.empty:

        return

    if len(result_df) < 2:

        st.info(
            "This result contains only one record. "
            "A chart is not necessary."
        )

        return

    numeric_columns = result_df.select_dtypes(
        include="number"
    ).columns.tolist()

    categorical_columns = result_df.select_dtypes(
        exclude="number"
    ).columns.tolist()

    if not numeric_columns:

        st.info(
            "No numerical columns available "
            "for automatic visualization."
        )

        return

    if not categorical_columns:

        st.info(
            "No categorical column is available "
            "to create a meaningful comparison chart."
        )

        return

    x_column = categorical_columns[0]
    y_column = numeric_columns[0]

    if result_df[x_column].nunique() > 30:

        st.info(
            "Too many categories for an automatic chart."
        )

        return

    chart_df = result_df.copy()

    fig = px.bar(
        chart_df,
        x=x_column,
        y=y_column,
        title=(
            f"{y_column.replace('_', ' ').title()} "
            f"by {x_column.replace('_', ' ').title()}"
        ),
        text_auto=True
    )

    fig.update_layout(
        xaxis_title=x_column.replace("_", " ").title(),
        yaxis_title=y_column.replace("_", " ").title(),
        xaxis_tickangle=-30
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ==================================================
# 21. USER QUESTION INPUT
# ==================================================

st.markdown("### Ask Your Database")

question = st.chat_input(
    "Example: Which market segment has the highest bookings?",
    key="ai_database_question"
)


# ==================================================
# 22. PROCESS USER QUESTION
# ==================================================

if question:

    st.session_state.ai_question_history.append({
        "role": "user",
        "content": question
    })

    if ask_database is None:

        response = {
            "success": False,
            "question": question,
            "generated_sql": None,
            "validated_sql": None,
            "results": None,
            "answer": None,
            "error": AI_IMPORT_ERROR
        }

    else:

        with st.spinner(
            "Gemini is generating SQL, SQL Guard is validating "
            "and MySQL is executing your query..."
        ):

            try:

                response = ask_database(question)

            except Exception as error:

                response = {
                    "success": False,
                    "question": question,
                    "generated_sql": None,
                    "validated_sql": None,
                    "results": None,
                    "answer": None,
                    "error": str(error)
                }

    st.session_state.ai_question_history.append({
        "role": "assistant",
        "response": response
    })


# ==================================================
# 23. DISPLAY AI CONVERSATION
# ==================================================

for message in st.session_state.ai_question_history:

    if message["role"] == "user":

        with st.chat_message("user"):

            st.write(message["content"])

    elif message["role"] == "assistant":

        response = message["response"]

        with st.chat_message("assistant"):

            if response.get("success"):

                st.success(
                    "Analysis completed successfully!"
                )

                # ----------------------------------
                # AI BUSINESS EXPLANATION
                # ----------------------------------

                st.markdown("### 🤖 AI Business Insights")

                st.markdown(
                    response.get("answer")
                    or "No explanation generated."
                )

                # ----------------------------------
                # MYSQL QUERY RESULTS
                # ----------------------------------

                st.markdown("### 📊 Actual MySQL Results")

                results = response.get("results")

                if results is not None:

                    result_df = pd.DataFrame(results)

                else:

                    result_df = pd.DataFrame()

                if not result_df.empty:

                    st.dataframe(
                        result_df,
                        use_container_width=True,
                        hide_index=True
                    )

                    # ----------------------------------
                    # AUTOMATIC VISUALIZATION
                    # ----------------------------------

                    st.markdown("### 📈 Query Visualization")

                    create_ai_chart(result_df)

                else:

                    st.info(
                        "The query returned no matching records."
                    )

                # ----------------------------------
                # GENERATED SQL
                # ----------------------------------

                with st.expander(
                    "🔍 View Gemini Generated SQL"
                ):

                    st.code(
                        response.get("generated_sql")
                        or "No SQL generated.",
                        language="sql"
                    )

                # ----------------------------------
                # VALIDATED SQL
                # ----------------------------------

                with st.expander(
                    "🛡️ View SQL Guard Validation"
                ):

                    if response.get("validated_sql"):

                        st.success(
                            "SQL Safety Check: PASSED"
                        )

                        st.code(
                            response["validated_sql"],
                            language="sql"
                        )

                    else:

                        st.warning(
                            "SQL validation was not completed."
                        )

            else:

                st.error(
                    "Unable to complete the analysis."
                )

                st.warning(
                    response.get("error")
                    or "Unknown error occurred."
                )

                if response.get("generated_sql"):

                    with st.expander(
                        "View Generated SQL"
                    ):

                        st.code(
                            response["generated_sql"],
                            language="sql"
                        )


# ==================================================
# 24. CLEAR AI CONVERSATION
# ==================================================

if st.session_state.ai_question_history:

    if st.button(
        "🗑️ Clear AI Conversation",
        key="clear_ai_history"
    ):

        st.session_state.ai_question_history = []

        st.rerun()


# ==================================================
# 25. FOOTER
# ==================================================

st.divider()

st.caption(
    "Booking Analytics & Intelligence Platform | "
    "Built with Python, MySQL, Streamlit, Plotly and Gemini AI"
)

st.caption(
    "Dataset: Kaggle Hotel Booking Demand. "
    "This is a public hotel dataset, not actual Amber "
    "or student accommodation booking data."
)

st.caption(
    "AI SQL execution uses the application's validation layer. "
    "Use a read-only MySQL account for database security."
)
