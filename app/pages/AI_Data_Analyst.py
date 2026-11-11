
import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parents[2]

if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.ai_analyst import ask_database


# --------------------------------------------------
# 2. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="AI Data Analyst",
    page_icon="🧠",
    layout="wide"
)

# --------------------------------------------------
# 3. PAGE HEADER
# --------------------------------------------------

st.title("🧠 AI Data Analyst")

st.caption(
    "Natural Language to SQL | Gemini AI | "
    "MySQL | SQL Safety Validation"
)

st.markdown(
    "Ask questions about hotel booking data "
    "using natural language. The AI generates SQL, "
    "validates it and retrieves actual database results."
)

st.divider()


# --------------------------------------------------
# 4. SAMPLE QUESTIONS
# --------------------------------------------------

st.markdown("### 💡 Try asking these questions")

col1, col2 = st.columns(2)

with col1:
    st.info(
        "Which market segment has the highest "
        "number of bookings?"
    )

    st.info(
        "Which country has the most bookings?"
    )

with col2:
    st.info(
        "What is the overall cancellation rate?"
    )

    st.info(
        "Which hotel has the highest average ADR?"
    )


st.divider()


# --------------------------------------------------
# 5. USER QUESTION INPUT
# --------------------------------------------------

st.markdown("### Ask Your Database")

if "ai_question_history" not in st.session_state:
    st.session_state.ai_question_history = []

question = st.chat_input(
    "Ask anything about hotel bookings..."
)


# --------------------------------------------------
# 6. PROCESS USER QUESTION
# --------------------------------------------------

if question:

    st.session_state.ai_question_history.append({
        "role": "user",
        "content": question
    })

    with st.chat_message("user"):
        st.write(question)

    with st.chat_message("assistant"):

        with st.spinner(
            "Generating SQL, validating query "
            "and analyzing database..."
        ):

            response = ask_database(question)

        if response["success"]:

            st.success("Analysis completed successfully!")

            # Natural language answer
            st.markdown("### 🤖 AI Answer")

            st.markdown(response["answer"])

            # Database results
            st.markdown("### 📊 Query Results")

            results = response["results"]

            if results:
                result_df = pd.DataFrame(results)

                st.dataframe(
                    result_df,
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.info("No matching records found.")

            # SQL details
            with st.expander("View Generated SQL"):

                st.code(
                    response["generated_sql"],
                    language="sql"
                )

            with st.expander("View SQL Safety Validation"):

                st.success("SQL Safety Check: PASSED")

                st.code(
                    response["validated_sql"],
                    language="sql"
                )

            st.session_state.ai_question_history.append({
                "role": "assistant",
                "content": response["answer"]
            })

        else:

            st.error("Unable to complete the analysis.")

            st.warning(response["error"])


# --------------------------------------------------
# 7. CONVERSATION HISTORY
# --------------------------------------------------

if st.session_state.ai_question_history:

    with st.expander("View Current Session History"):

        for message in st.session_state.ai_question_history:

            if message["role"] == "user":
                st.markdown(
                    f"**You:** {message['content']}"
                )
            else:
                st.markdown(
                    f"**AI Analyst:** {message['content']}"
                )


# --------------------------------------------------
# 8. FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "AI Data Analyst | Powered by Gemini, "
    "Python, MySQL and Streamlit"
)

st.caption(
    "SQL execution is restricted by the application's "
    "SQL validation layer and should use a read-only "
    "MySQL account."
)
