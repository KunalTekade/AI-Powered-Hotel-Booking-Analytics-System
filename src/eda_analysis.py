
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from pathlib import Path

# ==========================================
# 1. PATHS AND SETTINGS
# ==========================================

INPUT_FILE = Path("data/processed/hotel_bookings_cleaned.csv")
CHART_FOLDER = Path("reports/charts")
REPORT_FILE = Path("reports/eda_summary.txt")

CHART_FOLDER.mkdir(parents=True, exist_ok=True)
REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid")

# ==========================================
# 2. LOAD DATA
# ==========================================

df = pd.read_csv(INPUT_FILE)

df["arrival_date"] = pd.to_datetime(df["arrival_date"])
df["reservation_status_date"] = pd.to_datetime(
    df["reservation_status_date"]
)

print("\n========== PHASE 4: EDA ==========")
print("Dataset shape:", df.shape)

# ==========================================
# 3. KEY PERFORMANCE INDICATORS
# ==========================================

total_bookings = len(df)

cancelled_bookings = df["is_canceled"].sum()

successful_bookings = total_bookings - cancelled_bookings

cancellation_rate = (
    cancelled_bookings / total_bookings
) * 100

average_adr = df["adr"].mean()

average_lead_time = df["lead_time"].mean()

total_guests = df["total_guests"].sum()

# Estimated room value for non-cancelled bookings.
# This is not verified revenue or actual cash received.

non_cancelled = df[df["is_canceled"] == 0]

estimated_room_value = (
    non_cancelled["adr"] * non_cancelled["total_nights"]
).sum()

print("\n========== KEY BUSINESS METRICS ==========")

print("Total bookings:", total_bookings)
print("Cancelled bookings:", cancelled_bookings)
print("Non-cancelled bookings:", successful_bookings)
print(f"Cancellation rate: {cancellation_rate:.2f}%")
print(f"Average ADR: {average_adr:.2f}")
print(f"Average lead time: {average_lead_time:.2f} days")
print("Total guests:", total_guests)

print(
    "Estimated room value of non-cancelled bookings:",
    round(estimated_room_value, 2)
)

# ==========================================
# 4. HOTEL TYPE ANALYSIS
# ==========================================

hotel_bookings = df["hotel"].value_counts()

hotel_cancellations = (
    df.groupby("hotel")["is_canceled"].mean() * 100
)

print("\n========== HOTEL TYPE ANALYSIS ==========")
print("\nBookings by hotel:")
print(hotel_bookings)

print("\nCancellation rate by hotel (%):")
print(hotel_cancellations.round(2))

plt.figure(figsize=(8, 5))

sns.countplot(
    data=df,
    x="hotel",
    order=df["hotel"].value_counts().index
)

plt.title("Booking Distribution by Hotel Type")
plt.xlabel("Hotel Type")
plt.ylabel("Number of Bookings")

plt.savefig(
    CHART_FOLDER / "01_hotel_booking_distribution.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

# ==========================================
# 5. CANCELLATION ANALYSIS
# ==========================================

cancellation_data = df["is_canceled"].map({
    0: "Not Cancelled",
    1: "Cancelled"
})

plt.figure(figsize=(7, 5))

sns.countplot(
    x=cancellation_data,
    order=["Not Cancelled", "Cancelled"]
)

plt.title("Booking Cancellation Distribution")
plt.xlabel("Booking Status")
plt.ylabel("Number of Bookings")

plt.savefig(
    CHART_FOLDER / "02_cancellation_distribution.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

# Cancellation by market segment

segment_cancellation = (
    df.groupby("market_segment")["is_canceled"]
    .mean()
    .mul(100)
    .sort_values(ascending=False)
)

print("\n========== CANCELLATION BY MARKET SEGMENT ==========")
print(segment_cancellation.round(2))

plt.figure(figsize=(10, 6))

sns.barplot(
    x=segment_cancellation.values,
    y=segment_cancellation.index
)

plt.title("Cancellation Rate by Market Segment")
plt.xlabel("Cancellation Rate (%)")
plt.ylabel("Market Segment")

plt.savefig(
    CHART_FOLDER / "03_cancellation_by_segment.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

# ==========================================
# 6. MONTHLY BOOKING TREND
# ==========================================

df["arrival_month"] = df["arrival_date"].dt.to_period("M").astype(str)

monthly_bookings = (
    df.groupby("arrival_month")
    .size()
    .sort_index()
)

print("\n========== MONTHLY BOOKING TREND ==========")
print(monthly_bookings)

plt.figure(figsize=(15, 6))

monthly_bookings.plot(kind="line", marker="o")

plt.title("Monthly Booking Trend")
plt.xlabel("Arrival Month")
plt.ylabel("Number of Bookings")
plt.xticks(rotation=60)

plt.savefig(
    CHART_FOLDER / "04_monthly_booking_trend.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

# ==========================================
# 7. CUSTOMER TYPE ANALYSIS
# ==========================================

customer_bookings = (
    df["customer_type"]
    .value_counts()
)

print("\n========== CUSTOMER TYPE ANALYSIS ==========")
print(customer_bookings)

plt.figure(figsize=(9, 5))

sns.countplot(
    data=df,
    x="customer_type",
    order=customer_bookings.index
)

plt.title("Bookings by Customer Type")
plt.xlabel("Customer Type")
plt.ylabel("Number of Bookings")
plt.xticks(rotation=20)

plt.savefig(
    CHART_FOLDER / "05_customer_type_analysis.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

# ==========================================
# 8. COUNTRY ANALYSIS
# ==========================================

country_bookings = (
    df[df["country"] != "Unknown"]["country"]
    .value_counts()
    .head(10)
)

print("\n========== TOP 10 CUSTOMER COUNTRIES ==========")
print(country_bookings)

plt.figure(figsize=(10, 6))

sns.barplot(
    x=country_bookings.values,
    y=country_bookings.index
)

plt.title("Top 10 Countries by Booking Count")
plt.xlabel("Number of Bookings")
plt.ylabel("Country")

plt.savefig(
    CHART_FOLDER / "06_top_10_countries.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

# ==========================================
# 9. LEAD TIME ANALYSIS
# ==========================================

lead_time_cancel = (
    df.groupby("is_canceled")["lead_time"]
    .mean()
)

print("\n========== LEAD TIME ANALYSIS ==========")
print("Average lead time by cancellation status:")
print(lead_time_cancel)

plt.figure(figsize=(8, 5))

sns.boxplot(
    data=df,
    x="is_canceled",
    y="lead_time"
)

plt.title("Lead Time vs Cancellation Status")
plt.xlabel("Cancellation (0 = No, 1 = Yes)")
plt.ylabel("Lead Time (Days)")

plt.savefig(
    CHART_FOLDER / "07_lead_time_analysis.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

# ==========================================
# 10. ADR ANALYSIS
# ==========================================

adr_by_hotel = (
    df.groupby("hotel")["adr"]
    .mean()
)

print("\n========== ADR BY HOTEL ==========")
print(adr_by_hotel.round(2))

plt.figure(figsize=(8, 5))

sns.boxplot(
    data=df,
    x="hotel",
    y="adr"
)

plt.title("Average Daily Rate Distribution by Hotel")
plt.xlabel("Hotel Type")
plt.ylabel("ADR")

plt.savefig(
    CHART_FOLDER / "08_adr_by_hotel.png",
    dpi=300,
    bbox_inches="tight"
)

plt.close()

# ==========================================
# 11. WRITE EDA REPORT
# ==========================================

report = []

report.append("HOTEL BOOKING DATA - EDA REPORT")
report.append("=" * 50)

report.append(f"\nTotal bookings: {total_bookings}")
report.append(f"Cancelled bookings: {cancelled_bookings}")
report.append(f"Non-cancelled bookings: {successful_bookings}")
report.append(f"Cancellation rate: {cancellation_rate:.2f}%")
report.append(f"Average ADR: {average_adr:.2f}")
report.append(f"Average lead time: {average_lead_time:.2f} days")
report.append(f"Total guests: {total_guests}")

report.append(
    f"Estimated non-cancelled room value: {estimated_room_value:.2f}"
)

report.append("\nBOOKINGS BY HOTEL")
report.append(hotel_bookings.to_string())

report.append("\nCANCELLATION RATE BY HOTEL (%)")
report.append(hotel_cancellations.round(2).to_string())

report.append("\nCANCELLATION RATE BY MARKET SEGMENT (%)")
report.append(segment_cancellation.round(2).to_string())

report.append("\nTOP 10 COUNTRIES")
report.append(country_bookings.to_string())

report.append("\nAVERAGE LEAD TIME BY CANCELLATION STATUS")
report.append(lead_time_cancel.round(2).to_string())

report.append("\nAVERAGE ADR BY HOTEL")
report.append(adr_by_hotel.round(2).to_string())

REPORT_FILE.write_text(
    "\n".join(report),
    encoding="utf-8"
)

# ==========================================
# 12. COMPLETION
# ==========================================

print("\n========== EDA COMPLETED ==========")

print("Charts saved in:", CHART_FOLDER)
print("EDA report saved in:", REPORT_FILE)

print("\nGenerated charts:")

for chart in sorted(CHART_FOLDER.glob("*.png")):
    print("-", chart.name)

print("\nPHASE 4 COMPLETED!")
