
import joblib
import pandas as pd
import streamlit as st

from pathlib import Path


# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parents[2]

MODEL_PATH = (
    ROOT_DIR
    / "models"
    / "cancellation_prediction_pipeline.joblib"
)

DATA_PATH = (
    ROOT_DIR
    / "data"
    / "processed"
    / "hotel_bookings_cleaned.csv"
)


# --------------------------------------------------
# 2. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Cancellation Risk Predictor",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 Booking Cancellation Risk Predictor")

st.caption(
    "Machine Learning | Random Forest | Predictive Analytics"
)


# --------------------------------------------------
# 3. LOAD MODEL AND DATA OPTIONS
# --------------------------------------------------

@st.cache_resource
def load_model():
    return joblib.load(MODEL_PATH)


@st.cache_data
def load_options():

    data = pd.read_csv(
        DATA_PATH,
        usecols=[
            "country",
            "hotel",
            "meal",
            "market_segment",
            "distribution_channel",
            "reserved_room_type",
            "deposit_type",
            "customer_type"
        ]
    )

    data = data.fillna({
        "country": "Unknown"
    })

    return {
        column: sorted(
            data[column].dropna().astype(str).unique().tolist()
        )
        for column in data.columns
    }


try:
    model = load_model()
    options = load_options()

except Exception as error:
    st.error("Could not load the trained model or dataset.")
    st.code(str(error))
    st.stop()


# --------------------------------------------------
# 4. PREDICTION FORM
# --------------------------------------------------

st.markdown("### Enter Booking Information")

st.info(
    "This is a demonstration using historical Kaggle hotel "
    "booking data. Select arrival dates from July 2015 "
    "through August 2017, the period represented in this dataset."
)

with st.form("booking_prediction_form"):

    st.subheader("A. Hotel and Booking Details")

    col1, col2 = st.columns(2)

    with col1:

        hotel = st.selectbox(
            "Hotel",
            options["hotel"]
        )

        lead_time = st.number_input(
            "Lead Time (days)",
            min_value=0,
            max_value=1000,
            value=30
        )

        arrival_year = st.selectbox(
            "Arrival Year",
            [2015, 2016, 2017],
            index=1
        )

        arrival_month = st.selectbox(
            "Arrival Month",
            list(range(1, 13)),
            index=6
        )

        arrival_day = st.number_input(
            "Arrival Day",
            min_value=1,
            max_value=31,
            value=15
        )

    with col2:

        market_segment = st.selectbox(
            "Market Segment",
            options["market_segment"]
        )

        distribution_channel = st.selectbox(
            "Distribution Channel",
            options["distribution_channel"]
        )

        customer_type = st.selectbox(
            "Customer Type",
            options["customer_type"]
        )

        deposit_type = st.selectbox(
            "Deposit Type",
            options["deposit_type"]
        )

    st.divider()

    st.subheader("B. Guest Information")

    col1, col2, col3 = st.columns(3)

    with col1:
        adults = st.number_input(
            "Adults",
            min_value=0,
            max_value=20,
            value=2
        )

    with col2:
        children = st.number_input(
            "Children",
            min_value=0,
            max_value=20,
            value=0
        )

    with col3:
        babies = st.number_input(
            "Babies",
            min_value=0,
            max_value=10,
            value=0
        )

    col1, col2 = st.columns(2)

    with col1:
        is_repeated_guest = st.selectbox(
            "Repeated Guest?",
            [0, 1],
            format_func=lambda x: "Yes" if x == 1 else "No"
        )

        previous_cancellations = st.number_input(
            "Previous Cancellations",
            min_value=0,
            max_value=100,
            value=0
        )

        previous_bookings_not_canceled = st.number_input(
            "Previous Successful Bookings",
            min_value=0,
            max_value=100,
            value=0
        )

    with col2:
        country = st.selectbox(
            "Customer Country",
            options["country"],
            index=(
                options["country"].index("PRT")
                if "PRT" in options["country"] else 0
            )
        )

        meal = st.selectbox(
            "Meal Plan",
            options["meal"]
        )

        reserved_room_type = st.selectbox(
            "Reserved Room Type",
            options["reserved_room_type"]
        )

    st.divider()

    st.subheader("C. Stay and Pricing Information")

    col1, col2, col3 = st.columns(3)

    with col1:
        weekend_nights = st.number_input(
            "Weekend Nights",
            min_value=0,
            max_value=50,
            value=1
        )

    with col2:
        weekday_nights = st.number_input(
            "Weekday Nights",
            min_value=0,
            max_value=50,
            value=2
        )

    with col3:
        adr = st.number_input(
            "ADR (€)",
            min_value=0.0,
            max_value=10000.0,
            value=100.0,
            step=5.0
        )

    required_parking = st.number_input(
        "Required Car Parking Spaces",
        min_value=0,
        max_value=10,
        value=0
    )

    submitted = st.form_submit_button(
        "Predict Cancellation Risk",
        type="primary",
        use_container_width=True
    )


# --------------------------------------------------
# 5. PREDICTION
# --------------------------------------------------

if submitted:

    if adults + children + babies == 0:
        st.error("Please enter at least one guest.")

    elif weekend_nights + weekday_nights == 0:
        st.error("Please enter at least one night of stay.")

    else:

        input_data = pd.DataFrame([{

            "lead_time": lead_time,
            "arrival_date_year": arrival_year,
            "arrival_month": arrival_month,
            "arrival_day": arrival_day,
            "stays_in_weekend_nights": weekend_nights,
            "stays_in_week_nights": weekday_nights,
            "adults": adults,
            "children": children,
            "babies": babies,
            "is_repeated_guest": is_repeated_guest,
            "previous_cancellations": previous_cancellations,
            "previous_bookings_not_canceled":
                previous_bookings_not_canceled,
            "adr": adr,
            "required_car_parking_spaces": required_parking,

            "hotel": hotel,
            "meal": meal,
            "country": country,
            "market_segment": market_segment,
            "distribution_channel": distribution_channel,
            "reserved_room_type": reserved_room_type,
            "deposit_type": deposit_type,
            "customer_type": customer_type

        }])

        try:

            probability = model.predict_proba(
                input_data
            )[0][1]

            prediction = int(
                model.predict(input_data)[0]
            )

            st.divider()
            st.markdown("## Prediction Results")

            col1, col2 = st.columns(2)

            with col1:

                st.metric(
                    "Cancellation Probability",
                    f"{probability * 100:.2f}%"
                )

                st.progress(float(probability))

            with col2:

                if prediction == 1:
                    st.error("Higher predicted cancellation risk")
                else:
                    st.success("Lower predicted cancellation risk")

            st.caption(
                "The model uses its trained default classification "
                "threshold of 0.50. This is a prediction, not a guarantee."
            )

            st.markdown("### Prediction Interpretation")

            if probability >= 0.75:
                st.warning(
                    "The model estimates a high cancellation "
                    "probability for this booking."
                )

            elif probability >= 0.50:
                st.warning(
                    "The model estimates a moderate-to-high "
                    "cancellation probability."
                )

            else:
                st.success(
                    "The model estimates a lower cancellation "
                    "probability for this booking."
                )

            with st.expander("View submitted booking details"):
                st.dataframe(
                    input_data,
                    use_container_width=True,
                    hide_index=True
                )

        except Exception as error:
            st.error("Prediction failed.")
            st.code(str(error))


# --------------------------------------------------
# 6. FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "Model: Random Forest Classifier | "
    "Training dataset: Kaggle Hotel Booking Demand"
)
