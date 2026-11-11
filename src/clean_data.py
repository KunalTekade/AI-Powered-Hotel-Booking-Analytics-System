
import pandas as pd
from pathlib import Path

# -----------------------------------------
# 1. FILE PATHS
# -----------------------------------------

RAW_FILE = Path("data/raw/hotel_bookings.csv")
PROCESSED_FOLDER = Path("data/processed")

PROCESSED_FOLDER.mkdir(parents=True, exist_ok=True)

OUTPUT_FILE = PROCESSED_FOLDER / "hotel_bookings_cleaned.csv"
REPORT_FILE = Path("reports/data_cleaning_report.txt")

REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)

# -----------------------------------------
# 2. LOAD ORIGINAL DATA
# -----------------------------------------

print("\n========== PHASE 3: DATA CLEANING ==========")

df = pd.read_csv(RAW_FILE)

original_rows = len(df)

print("Original dataset shape:", df.shape)

# -----------------------------------------
# 3. REMOVE EXACT DUPLICATES
# -----------------------------------------

duplicate_count = df.duplicated().sum()

df = df.drop_duplicates().copy()

print("Duplicate rows removed:", duplicate_count)
print("Rows after duplicate removal:", len(df))

# -----------------------------------------
# 4. HANDLE MISSING VALUES
# -----------------------------------------

# Children: assume missing means zero children
df["children"] = df["children"].fillna(0)

# Country: retain missing information as Unknown
df["country"] = df["country"].fillna("Unknown")

# Agent and company:
# Keep missing IDs as NaN.
# Create indicators to identify their absence.

df["has_agent"] = df["agent"].notna().astype(int)
df["has_company"] = df["company"].notna().astype(int)

# -----------------------------------------
# 5. CONVERT DATA TYPES
# -----------------------------------------

df["children"] = df["children"].astype(int)

df["agent"] = pd.to_numeric(df["agent"], errors="coerce")
df["company"] = pd.to_numeric(df["company"], errors="coerce")

# Convert reservation status date
df["reservation_status_date"] = pd.to_datetime(
    df["reservation_status_date"],
    errors="coerce"
)

# Create a complete arrival date
df["arrival_date"] = pd.to_datetime(
    df["arrival_date_year"].astype(str)
    + "-"
    + df["arrival_date_month"]
    + "-"
    + df["arrival_date_day_of_month"].astype(str),
    format="%Y-%B-%d",
    errors="coerce"
)

# -----------------------------------------
# 6. CREATE USEFUL ANALYTICAL COLUMNS
# -----------------------------------------

# Total guests
df["total_guests"] = (
    df["adults"] + df["children"] + df["babies"]
)

# Total nights stayed
df["total_nights"] = (
    df["stays_in_weekend_nights"]
    + df["stays_in_week_nights"]
)

# Estimated booking revenue
df["estimated_revenue"] = df["adr"] * df["total_nights"]

# Booking month and year
df["arrival_month_number"] = df["arrival_date"].dt.month
df["arrival_year"] = df["arrival_date"].dt.year

# Create a project-level booking ID.
# This is an assigned identifier, not an original Kaggle ID.

df = df.reset_index(drop=True)
df.insert(
    0,
    "booking_id",
    ["BK" + str(i).zfill(6) for i in range(1, len(df) + 1)]
)

# -----------------------------------------
# 7. DATA QUALITY CHECKS
# -----------------------------------------

negative_adr = (df["adr"] < 0).sum()

zero_guest_bookings = (df["total_guests"] == 0).sum()

zero_night_bookings = (df["total_nights"] == 0).sum()

invalid_arrival_dates = df["arrival_date"].isna().sum()

remaining_duplicates = df.drop(columns=["booking_id"]).duplicated().sum()

missing_values = df.isnull().sum()

# -----------------------------------------
# 8. SAVE CLEANED DATASET
# -----------------------------------------

df.to_csv(OUTPUT_FILE, index=False)

# -----------------------------------------
# 9. GENERATE CLEANING REPORT
# -----------------------------------------

report = []

report.append("HOTEL BOOKING DATA - CLEANING REPORT")
report.append("=" * 45)

report.append(f"Original records: {original_rows}")
report.append(f"Duplicate rows removed: {duplicate_count}")
report.append(f"Cleaned records: {len(df)}")
report.append(f"Columns after cleaning: {len(df.columns)}")

report.append("\nMISSING VALUE COUNTS AFTER CLEANING")
report.append("-" * 45)
report.append(missing_values.to_string())

report.append("\nDATA QUALITY CHECKS")
report.append("-" * 45)
report.append(f"Negative ADR records: {negative_adr}")
report.append(f"Zero-guest bookings: {zero_guest_bookings}")
report.append(f"Zero-night bookings: {zero_night_bookings}")
report.append(f"Invalid arrival dates: {invalid_arrival_dates}")
report.append(f"Remaining exact duplicate rows: {remaining_duplicates}")

report.append("\nOUTPUT FILE")
report.append(str(OUTPUT_FILE))

REPORT_FILE.write_text("\n".join(report), encoding="utf-8")

# -----------------------------------------
# 10. DISPLAY RESULTS
# -----------------------------------------

print("\n========== CLEANING SUMMARY ==========")

print("Original records:", original_rows)
print("Duplicates removed:", duplicate_count)
print("Cleaned records:", len(df))
print("Final columns:", len(df.columns))

print("\nMissing values after cleaning:")
print(missing_values[missing_values > 0])

print("\nData quality checks:")
print("Negative ADR:", negative_adr)
print("Zero guests:", zero_guest_bookings)
print("Zero nights:", zero_night_bookings)
print("Invalid arrival dates:", invalid_arrival_dates)
print("Remaining duplicates:", remaining_duplicates)

print("\nCleaned dataset saved at:", OUTPUT_FILE)
print("Cleaning report saved at:", REPORT_FILE)

print("\nPHASE 3 CLEANING COMPLETED!")
