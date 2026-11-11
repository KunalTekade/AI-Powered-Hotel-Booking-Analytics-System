
import streamlit as st

st.set_page_config(
    page_title="Booking Analytics Platform",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Booking Analytics & Intelligence Platform")

st.markdown("""
### Welcome to your Hotel Booking Analytics Platform

Explore three analytical capabilities:

**1. Business Intelligence Dashboard**
- Booking trends
- Hotel performance
- Customer and geographical analysis

**2. Cancellation Risk Predictor**
- Random Forest classification
- Cancellation probability
- Booking risk assessment

**3. AI Data Analyst**
- Natural language queries
- Gemini SQL generation
- SQL safety validation
- Live MySQL query execution
- AI-generated explanations
""")

st.info(
    "Select a page from the navigation sidebar "
    "to begin your analysis."
)
