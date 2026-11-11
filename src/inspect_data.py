
import pandas as pd
from pathlib import Path

# Dataset location
file_path = Path("data/raw/hotel_bookings.csv")

# Check whether file exists
if not file_path.exists():
    print("Dataset not found! Check the file location.")
else:
    df = pd.read_csv(file_path)

    print("\n========== DATASET INFORMATION ==========")

    print("\nShape (Rows, Columns):")
    print(df.shape)

    print("\nFirst 5 Records:")
    print(df.head())

    print("\nColumn Names:")
    print(df.columns.tolist())

    print("\nData Types:")
    print(df.dtypes)

    print("\nMissing Values:")
    print(df.isnull().sum())

    print("\nDuplicate Records:")
    print(df.duplicated().sum())

    print("\nDataset Loaded Successfully!")
