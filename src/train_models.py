import pandas as pd
import numpy as np
import time
import joblib

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from lightgbm import LGBMRegressor
from xgboost import XGBRegressor
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

# -----------------------------------------
# 1. Load processed dataset
# -----------------------------------------

data = pd.read_csv(
    BASE_DIR / "outputs" / "processed_traffic_data.csv"
)

print("Processed dataset loaded successfully")
print("Dataset shape:", data.shape)


# -----------------------------------------
# 2. Convert date_time
# -----------------------------------------

data["date_time"] = pd.to_datetime(data["date_time"])


# -----------------------------------------
# 3. Encode categorical columns
# -----------------------------------------

data = pd.get_dummies(
    data,
    columns=[
        "holiday",
        "weather_main",
        "weather_description"
    ],
    dtype=int
)


# -----------------------------------------
# 4. Separate features and target
# -----------------------------------------

X = data.drop(
    columns=[
        "traffic_volume",
        "date_time"
    ]
)

y = data["traffic_volume"]


print("\nNumber of features:", X.shape[1])
print("Target:", "traffic_volume")


# -----------------------------------------
# 5. Chronological train-test split
# -----------------------------------------

split = int(len(data) * 0.80)

X_train = X.iloc[:split]
X_test = X.iloc[split:]

y_train = y.iloc[:split]
y_test = y.iloc[split:]


print("\nTraining data:", X_train.shape)
print("Testing data:", X_test.shape)


# -----------------------------------------
# 6. Train LightGBM
# -----------------------------------------

print("\n============================")
print("Training LightGBM")
print("==============================")


lightgbm_model = LGBMRegressor(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=8,
    num_leaves=31,
    random_state=42,
    verbosity=-1
)


start_time = time.time()

lightgbm_model.fit(
    X_train,
    y_train
)

lightgbm_training_time = time.time() - start_time


# Predictions

lightgbm_train_pred = lightgbm_model.predict(X_train)

lightgbm_test_pred = lightgbm_model.predict(X_test)


# Metrics

lightgbm_train_mae = mean_absolute_error(
    y_train,
    lightgbm_train_pred
)

lightgbm_test_mae = mean_absolute_error(
    y_test,
    lightgbm_test_pred
)


lightgbm_train_rmse = np.sqrt(
    mean_squared_error(
        y_train,
        lightgbm_train_pred
    )
)

lightgbm_test_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        lightgbm_test_pred
    )
)


lightgbm_train_r2 = r2_score(
    y_train,
    lightgbm_train_pred
)

lightgbm_test_r2 = r2_score(
    y_test,
    lightgbm_test_pred
)


print("\nLightGBM Results")

print("Training Time:",
      round(lightgbm_training_time, 2),
      "seconds")

print("Train MAE:",
      round(lightgbm_train_mae, 2))

print("Test MAE:",
      round(lightgbm_test_mae, 2))

print("Train RMSE:",
      round(lightgbm_train_rmse, 2))

print("Test RMSE:",
      round(lightgbm_test_rmse, 2))

print("Train R2:",
      round(lightgbm_train_r2, 4))

print("Test R2:",
      round(lightgbm_test_r2, 4))


# -----------------------------------------
# 7. Train XGBoost
# -----------------------------------------

print("\n============================")
print("Training XGBoost")
print("==============================")


xgboost_model = XGBRegressor(
    n_estimators=300,
    learning_rate=0.05,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    objective="reg:squarederror"
)


start_time = time.time()

xgboost_model.fit(
    X_train,
    y_train
)

xgboost_training_time = time.time() - start_time


# Predictions

xgboost_train_pred = xgboost_model.predict(X_train)

xgboost_test_pred = xgboost_model.predict(X_test)


# Metrics

xgboost_train_mae = mean_absolute_error(
    y_train,
    xgboost_train_pred
)

xgboost_test_mae = mean_absolute_error(
    y_test,
    xgboost_test_pred
)


xgboost_train_rmse = np.sqrt(
    mean_squared_error(
        y_train,
        xgboost_train_pred
    )
)

xgboost_test_rmse = np.sqrt(
    mean_squared_error(
        y_test,
        xgboost_test_pred
    )
)


xgboost_train_r2 = r2_score(
    y_train,
    xgboost_train_pred
)

xgboost_test_r2 = r2_score(
    y_test,
    xgboost_test_pred
)


print("\nXGBoost Results")

print("Training Time:",
      round(xgboost_training_time, 2),
      "seconds")

print("Train MAE:",
      round(xgboost_train_mae, 2))

print("Test MAE:",
      round(xgboost_test_mae, 2))

print("Train RMSE:",
      round(xgboost_train_rmse, 2))

print("Test RMSE:",
      round(xgboost_test_rmse, 2))

print("Train R2:",
      round(xgboost_train_r2, 4))

print("Test R2:",
      round(xgboost_test_r2, 4))


# -----------------------------------------
# 8. Compare models
# -----------------------------------------

comparison = pd.DataFrame({

    "Model": [
        "LightGBM",
        "XGBoost"
    ],

    "Train MAE": [
        lightgbm_train_mae,
        xgboost_train_mae
    ],

    "Test MAE": [
        lightgbm_test_mae,
        xgboost_test_mae
    ],

    "Train RMSE": [
        lightgbm_train_rmse,
        xgboost_train_rmse
    ],

    "Test RMSE": [
        lightgbm_test_rmse,
        xgboost_test_rmse
    ],

    "Train R2": [
        lightgbm_train_r2,
        xgboost_train_r2
    ],

    "Test R2": [
        lightgbm_test_r2,
        xgboost_test_r2
    ],

    "Training Time": [
        lightgbm_training_time,
        xgboost_training_time
    ]
})


print("\n============================")
print("MODEL COMPARISON")
print("==============================")

print(comparison.to_string(index=False))


# -----------------------------------------
# 9. Check overfitting
# -----------------------------------------

print("\n============================")
print("OVERFITTING CHECK")
print("==============================")


lightgbm_r2_gap = (
    lightgbm_train_r2 -
    lightgbm_test_r2
)

xgboost_r2_gap = (
    xgboost_train_r2 -
    xgboost_test_r2
)


print(
    "LightGBM R2 Gap:",
    round(lightgbm_r2_gap, 4)
)

print(
    "XGBoost R2 Gap:",
    round(xgboost_r2_gap, 4)
)


# -----------------------------------------
# 10. Feature importance
# -----------------------------------------

importance = pd.DataFrame({

    "Feature": X_train.columns,

    "Importance": lightgbm_model.feature_importances_

})


importance = importance.sort_values(
    "Importance",
    ascending=False
)


print("\nTop 15 important features:")

print(
    importance.head(15).to_string(index=False)
)


# -----------------------------------------
# 11. Save model comparison
# -----------------------------------------

comparison.to_csv(
    "outputs/model_comparison.csv",
    index=False
)


# -----------------------------------------
# 12. Save feature importance
# -----------------------------------------

importance.to_csv(
    "outputs/feature_importance.csv",
    index=False
)


# -----------------------------------------
# 13. Save trained models
# -----------------------------------------

joblib.dump(
    lightgbm_model,
    "models/lightgbm_model.pkl"
)


joblib.dump(
    xgboost_model,
    "models/xgboost_model.pkl"
)


print("\n==============================")
print("FILES SAVED SUCCESSFULLY")
print("==============================")

print("outputs/model_comparison.csv")
print("outputs/feature_importance.csv")
print("models/lightgbm_model.pkl")
print("models/xgboost_model.pkl")   