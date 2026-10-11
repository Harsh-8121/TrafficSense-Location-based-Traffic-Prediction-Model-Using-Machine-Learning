import pandas as pd


# -----------------------------------------
# 1. Load dataset
# -----------------------------------------

data = pd.read_csv("data/Metro_Interstate_Traffic_Volume.csv")

print("Dataset loaded successfully")
print("Original shape:", data.shape)


# -----------------------------------------
# 2. Remove duplicate rows
# -----------------------------------------

duplicate_count = data.duplicated().sum()

print("\nDuplicate rows found:", duplicate_count)

data = data.drop_duplicates()

print("Shape after removing duplicates:", data.shape)


# -----------------------------------------
# 3. Convert date_time
# -----------------------------------------

data["date_time"] = pd.to_datetime(
    data["date_time"],
    dayfirst=True
)


# -----------------------------------------
# 4. Sort according to time
# -----------------------------------------

data = data.sort_values("date_time")

data = data.reset_index(drop=True)


print("\nEarliest date:")
print(data["date_time"].min())

print("\nLatest date:")
print(data["date_time"].max())


# -----------------------------------------
# 5. Handle missing holiday values
# -----------------------------------------

data["holiday"] = data["holiday"].fillna("None")


# -----------------------------------------
# 6. Create time-based features
# -----------------------------------------

data["year"] = data["date_time"].dt.year

data["month"] = data["date_time"].dt.month

data["day"] = data["date_time"].dt.day

data["hour"] = data["date_time"].dt.hour

data["day_of_week"] = data["date_time"].dt.dayofweek

data["is_weekend"] = (
    data["day_of_week"] >= 5
).astype(int)


# Peak traffic hours

data["is_peak_hour"] = data["hour"].isin(
    [7, 8, 9, 16, 17, 18]
).astype(int)


# -----------------------------------------
# 7. Create a separate hourly dataset
# -----------------------------------------

hourly_data = (
    data.groupby("date_time", as_index=False)
    .agg({
        "traffic_volume": "mean",
        "temp": "mean",
        "rain_1h": "mean",
        "snow_1h": "mean",
        "clouds_all": "mean",
        "holiday": "first",
        "weather_main": "first",
        "weather_description": "first",
        "year": "first",
        "month": "first",
        "day": "first",
        "hour": "first",
        "day_of_week": "first",
        "is_weekend": "first",
        "is_peak_hour": "first"
    })
)


hourly_data = hourly_data.sort_values("date_time")

hourly_data = hourly_data.reset_index(drop=True)


print("\nHourly dataset shape:")
print(hourly_data.shape)


# -----------------------------------------
# 8. Create time-aware lag features
# -----------------------------------------

hourly_data["traffic_lag_1h"] = (
    hourly_data["traffic_volume"]
    .shift(1)
)

hourly_data["traffic_lag_2h"] = (
    hourly_data["traffic_volume"]
    .shift(2)
)

hourly_data["traffic_lag_24h"] = (
    hourly_data["traffic_volume"]
    .shift(24)
)

hourly_data["traffic_lag_168h"] = (
    hourly_data["traffic_volume"]
    .shift(168)
)


# -----------------------------------------
# 9. Check timestamp continuity
# -----------------------------------------

time_difference = hourly_data["date_time"].diff()

print("\nTime differences after grouping:")
print(time_difference.value_counts().head(10))


# -----------------------------------------
# 10. Remove rows with unavailable lags
# -----------------------------------------

hourly_data = hourly_data.dropna(
    subset=[
        "traffic_lag_1h",
        "traffic_lag_2h",
        "traffic_lag_24h",
        "traffic_lag_168h"
    ]
)


hourly_data = hourly_data.reset_index(drop=True)


# -----------------------------------------
# 11. Final dataset information
# -----------------------------------------

print("\nFinal dataset shape:")
print(hourly_data.shape)


print("\nFinal columns:")
print(hourly_data.columns.tolist())


print("\nFirst 5 rows:")
print(hourly_data.head())

# Save processed dataset

hourly_data.to_csv(
    "outputs/processed_traffic_data.csv",
    index=False
)

print("\nProcessed dataset saved successfully!")