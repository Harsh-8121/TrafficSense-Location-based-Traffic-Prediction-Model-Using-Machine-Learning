import pandas as pd
import joblib
import oracledb
import os
from dotenv import load_dotenv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


load_dotenv()

print("==============================")
print("TRAFFIC VOLUME PREDICTION APP")
print("==============================")

# Load processed dataset
data = pd.read_csv(
    BASE_DIR / "outputs" / "processed_traffic_data.csv"
)

# Convert date_time
data["date_time"] = pd.to_datetime(data["date_time"])

# Load LightGBM model
model = joblib.load("models/lightgbm_model.pkl")

print("\nLightGBM model loaded successfully!")

# Ask user for date and time
date_input = input("\nEnter date (YYYY-MM-DD): ")
time_input = input("Enter time (HH:MM): ")

selected_datetime = pd.to_datetime(
    date_input + " " + time_input
)

# Find matching record
record = data[data["date_time"] == selected_datetime]

if len(record) == 0:

    print("\nNo matching record found in the processed dataset.")
    print("Please enter a date and time available in the dataset.")

else:

    # Make a copy
    prediction_record = record.copy()

    # Store actual traffic
    actual_traffic = prediction_record["traffic_volume"].iloc[0]

    # One-hot encoding
    prediction_record = pd.get_dummies(
        prediction_record,
        columns=[
            "holiday",
            "weather_main",
            "weather_description"
        ],
        dtype=int
    )

    # Remove target and date
    X = prediction_record.drop(
        columns=[
            "traffic_volume",
            "date_time"
        ]
    )

    # Make sure feature columns match training model
    model_features = model.feature_name_

    for feature in model_features:

        if feature not in X.columns:
            X[feature] = 0

    # Keep exactly the same feature order
    X = X[model_features]

    # Predict
    predicted_traffic = model.predict(X)[0]

    predicted_traffic = round(predicted_traffic)

    print("\n==============================")
    print("PREDICTION RESULT")
    print("==============================")

    print("Date and Time:", selected_datetime)
    print("Actual Traffic:", actual_traffic)
    print("Predicted Traffic:", predicted_traffic)

    prediction_error = abs(
        actual_traffic - predicted_traffic
    )

    print("Prediction Error:", prediction_error)

    # Oracle connection
    username = os.getenv("ORACLE_USER")
    password = os.getenv("ORACLE_PASSWORD")
    dsn = os.getenv("ORACLE_DSN", "localhost:1521/xe")

    connection = oracledb.connect(
        user=username,
        password=password,
        dsn=dsn
    )

    cursor = connection.cursor()

    # Store prediction in Oracle
    cursor.execute(
        """
        INSERT INTO TRAFFIC_PREDICTIONS
        (
            date_time,
            actual_traffic_volume,
            predicted_traffic_volume
        )
        VALUES
        (
            :1,
            :2,
            :3
        )
        """,
        (
            selected_datetime.to_pydatetime(),
            float(actual_traffic),
            float(predicted_traffic)
        )
    )

    connection.commit()

    print("\nPrediction stored in Oracle successfully!")

    cursor.close()
    connection.close()

    print("Oracle connection closed.")