
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import joblib

from pathlib import Path

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report,
    ConfusionMatrixDisplay,
    RocCurveDisplay
)


# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

ROOT_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = ROOT_DIR / "data" / "processed" / "hotel_bookings_cleaned.csv"

MODEL_DIR = ROOT_DIR / "models"
REPORT_DIR = ROOT_DIR / "reports"
CHART_DIR = REPORT_DIR / "charts"

MODEL_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)
CHART_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. LOAD DATA
# --------------------------------------------------

print("\n" + "=" * 55)
print("BOOKING CANCELLATION PREDICTION MODEL")
print("=" * 55)

df = pd.read_csv(DATA_PATH)

print("\nDataset loaded successfully!")
print("Dataset shape:", df.shape)


# --------------------------------------------------
# 3. DATA PREPARATION
# --------------------------------------------------

df["arrival_date"] = pd.to_datetime(
    df["arrival_date"], errors="coerce"
)

# Extract arrival date information
df["arrival_month"] = df["arrival_date"].dt.month
df["arrival_day"] = df["arrival_date"].dt.day

# Target variable
TARGET = "is_canceled"

# Features available at or around booking creation.
# Exclude post-booking information to reduce leakage.

numerical_features = [
    "lead_time",
    "arrival_date_year",
    "arrival_month",
    "arrival_day",
    "stays_in_weekend_nights",
    "stays_in_week_nights",
    "adults",
    "children",
    "babies",
    "is_repeated_guest",
    "previous_cancellations",
    "previous_bookings_not_canceled",
    "adr",
    "required_car_parking_spaces"
]

categorical_features = [
    "hotel",
    "meal",
    "country",
    "market_segment",
    "distribution_channel",
    "reserved_room_type",
    "deposit_type",
    "customer_type"
]

feature_columns = numerical_features + categorical_features

required_columns = feature_columns + [TARGET]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    raise ValueError(
        f"Missing required columns: {missing_columns}"
    )

# Remove records without a valid target
df = df.dropna(subset=[TARGET]).copy()

X = df[feature_columns]
y = df[TARGET].astype(int)

print("\nTarget distribution:")
print(y.value_counts())

print("\nFeatures used:", len(feature_columns))


# --------------------------------------------------
# 4. TRAIN-TEST SPLIT
# --------------------------------------------------

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

print("\nTraining records:", len(X_train))
print("Testing records:", len(X_test))


# --------------------------------------------------
# 5. PREPROCESSING
# --------------------------------------------------

numerical_pipeline = Pipeline(
    steps=[
        ("imputer", SimpleImputer(strategy="median"))
    ]
)

categorical_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(
                strategy="most_frequent"
            )
        ),
        (
            "encoder",
            OneHotEncoder(
                handle_unknown="ignore",
                min_frequency=10
            )
        )
    ]
)

preprocessor = ColumnTransformer(
    transformers=[
        (
            "numerical",
            numerical_pipeline,
            numerical_features
        ),
        (
            "categorical",
            categorical_pipeline,
            categorical_features
        )
    ]
)


# --------------------------------------------------
# 6. RANDOM FOREST MODEL
# --------------------------------------------------

random_forest = RandomForestClassifier(
    n_estimators=200,
    max_depth=16,
    min_samples_split=10,
    min_samples_leaf=3,
    class_weight="balanced_subsample",
    random_state=42,
    n_jobs=-1
)

model = Pipeline(
    steps=[
        ("preprocessor", preprocessor),
        ("classifier", random_forest)
    ]
)


# --------------------------------------------------
# 7. MODEL TRAINING
# --------------------------------------------------

print("\nTraining Random Forest model...")

model.fit(X_train, y_train)

print("Model training completed!")


# --------------------------------------------------
# 8. MODEL EVALUATION
# --------------------------------------------------

y_pred = model.predict(X_test)

y_probability = model.predict_proba(X_test)[:, 1]

accuracy = accuracy_score(y_test, y_pred)

precision = precision_score(
    y_test, y_pred, zero_division=0
)

recall = recall_score(
    y_test, y_pred, zero_division=0
)

f1 = f1_score(
    y_test, y_pred, zero_division=0
)

roc_auc = roc_auc_score(
    y_test, y_probability
)

print("\n" + "=" * 55)
print("MODEL PERFORMANCE")
print("=" * 55)

print(f"Accuracy:  {accuracy:.4f}")
print(f"Precision: {precision:.4f}")
print(f"Recall:    {recall:.4f}")
print(f"F1 Score:  {f1:.4f}")
print(f"ROC-AUC:   {roc_auc:.4f}")

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        y_pred,
        target_names=["Not Cancelled", "Cancelled"],
        zero_division=0
    )
)


# --------------------------------------------------
# 9. CONFUSION MATRIX
# --------------------------------------------------

cm = confusion_matrix(y_test, y_pred)

display = ConfusionMatrixDisplay(
    confusion_matrix=cm,
    display_labels=["Not Cancelled", "Cancelled"]
)

display.plot(cmap="Blues", values_format="d")

plt.title("Booking Cancellation - Confusion Matrix")
plt.tight_layout()

plt.savefig(
    CHART_DIR / "09_cancellation_confusion_matrix.png",
    dpi=300
)

plt.close()


# --------------------------------------------------
# 10. ROC CURVE
# --------------------------------------------------

fig, ax = plt.subplots(figsize=(8, 6))

RocCurveDisplay.from_predictions(
    y_test,
    y_probability,
    ax=ax
)

ax.set_title("Random Forest - ROC Curve")

plt.tight_layout()

plt.savefig(
    CHART_DIR / "10_cancellation_roc_curve.png",
    dpi=300
)

plt.close()


# --------------------------------------------------
# 11. FEATURE IMPORTANCE
# --------------------------------------------------

fitted_preprocessor = model.named_steps["preprocessor"]

feature_names = fitted_preprocessor.get_feature_names_out()

importance_values = (
    model.named_steps["classifier"].feature_importances_
)

importance_df = pd.DataFrame({
    "feature": feature_names,
    "importance": importance_values
})

importance_df = importance_df.sort_values(
    by="importance",
    ascending=False
)

top_features = importance_df.head(20).sort_values(
    by="importance"
)

plt.figure(figsize=(11, 8))

plt.barh(
    top_features["feature"],
    top_features["importance"]
)

plt.title("Top 20 Features Influencing Cancellation Predictions")
plt.xlabel("Feature Importance")
plt.ylabel("Feature")

plt.tight_layout()

plt.savefig(
    CHART_DIR / "11_cancellation_feature_importance.png",
    dpi=300
)

plt.close()


# --------------------------------------------------
# 12. SAVE MODEL
# --------------------------------------------------

MODEL_PATH = MODEL_DIR / "cancellation_prediction_pipeline.joblib"

joblib.dump(model, MODEL_PATH)

print("\nSaved trained model:")
print(MODEL_PATH)


# --------------------------------------------------
# 13. SAVE EVALUATION REPORT
# --------------------------------------------------

report_path = REPORT_DIR / "cancellation_model_report.txt"

with open(report_path, "w", encoding="utf-8") as file:

    file.write("BOOKING CANCELLATION PREDICTION REPORT\n")
    file.write("=" * 50 + "\n\n")

    file.write(f"Dataset records: {len(df)}\n")
    file.write(f"Training records: {len(X_train)}\n")
    file.write(f"Testing records: {len(X_test)}\n\n")

    file.write("MODEL: RANDOM FOREST CLASSIFIER\n\n")

    file.write(f"Accuracy: {accuracy:.4f}\n")
    file.write(f"Precision: {precision:.4f}\n")
    file.write(f"Recall: {recall:.4f}\n")
    file.write(f"F1 Score: {f1:.4f}\n")
    file.write(f"ROC-AUC: {roc_auc:.4f}\n\n")

    file.write("CLASSIFICATION REPORT\n")
    file.write(
        classification_report(
            y_test,
            y_pred,
            target_names=["Not Cancelled", "Cancelled"],
            zero_division=0
        )
    )

    file.write("\nTOP 20 FEATURES\n")
    file.write(importance_df.head(20).to_string(index=False))

print("\nEvaluation report saved:", report_path)

print("\n" + "=" * 55)
print("PHASE 8 - MODEL TRAINING COMPLETED!")
print("=" * 55)
