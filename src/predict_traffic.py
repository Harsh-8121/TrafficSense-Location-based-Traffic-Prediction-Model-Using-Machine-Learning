import pandas as pd
import joblib

print("==============================")
print("TRAFFIC VOLUME PREDICTION")
print("==============================")

# Load processed dataset
data = pd.read_csv("outputs/processed_traffic_data.csv")

# Convert date_time
data["date_time"] = pd.to_datetime(data["date_time"])

# One-hot encoding
data = pd.get_dummies(
    data,
    columns=["holiday", "weather_main", "weather_description"],
    dtype=int
)

# Separate features and target
X = data.drop(columns=["traffic_volume", "date_time"])
y = data["traffic_volume"]

# Load trained LightGBM model
model = joblib.load("models/lightgbm_model.pkl")

print("\nLightGBM model loaded successfully!")

# Make predictions
predictions = model.predict(X)

# Create prediction table
prediction_data = pd.DataFrame()

prediction_data["date_time"] = data["date_time"]
prediction_data["actual_traffic_volume"] = y
prediction_data["predicted_traffic_volume"] = predictions

# Round predictions
prediction_data["predicted_traffic_volume"] = (
    prediction_data["predicted_traffic_volume"].round(0)
)

print("\nPrediction completed successfully!")

print("\nFirst 10 predictions:")
print(prediction_data.head(10))

# Save predictions
prediction_data.to_csv(
    "outputs/traffic_predictions.csv",
    index=False
)

print("\nPredictions saved successfully!")
print("File: outputs/traffic_predictions.csv")