from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import pandas as pd
import joblib
import oracledb

from pathlib import Path

import os
from dotenv import load_dotenv

load_dotenv()


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_FILE = BASE_DIR / "outputs" / "processed_traffic_data.csv"
MODEL_FILE = BASE_DIR / "models" / "lightgbm_model.pkl"


# ============================================================
# LOAD DATA
# ============================================================

print("Loading processed traffic data...")

data = pd.read_csv(DATA_FILE)

data["date_time"] = pd.to_datetime(data["date_time"])

print("Processed traffic data loaded successfully.")


# ============================================================
# LOAD MODEL
# ============================================================

print("Loading LightGBM model...")

model = joblib.load(MODEL_FILE)

print("LightGBM model loaded successfully.")


# ============================================================
# CREATE FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="TrafficSense API",
    description="Traffic Volume Prediction API",
    version="1.0"
)


# ============================================================
# CORS
# ============================================================

FRONTEND_URL = os.getenv("FRONTEND_URL", "")

ALLOWED_ORIGINS = [
    "http://127.0.0.1:5501",
    "http://localhost:5501",
]

if FRONTEND_URL:
    ALLOWED_ORIGINS.append(FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,

    allow_origins=ALLOWED_ORIGINS,

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


# ============================================================
# ORACLE SETTINGS
# ============================================================

ORACLE_USERNAME = os.getenv("ORACLE_USER")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD")
ORACLE_DSN = os.getenv("ORACLE_DSN", "localhost:1521/xe")



# ============================================================
# ORACLE CONNECTION
# ============================================================

def get_oracle_connection():

    connection = oracledb.connect(
        user=ORACLE_USERNAME,
        password=ORACLE_PASSWORD,
        dsn=ORACLE_DSN
    )

    return connection


# ============================================================
# HOME
# ============================================================

@app.get("/")
def home():

    return {
        "message": "TrafficSense API is running",
        "model": "LightGBM",
        "status": "online"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy",
        "model_loaded": True,
        "dataset_loaded": True
    }


# ============================================================
# PREDICTION
# ============================================================

@app.post("/predict")
def predict_traffic(date: str, time: str):

    try:

        # ----------------------------------------------------
        # Convert date and time
        # ----------------------------------------------------

        requested_datetime = pd.to_datetime(
            date + " " + time
        )


        # ----------------------------------------------------
        # Find matching record
        # ----------------------------------------------------

        matching_rows = data[
            data["date_time"] == requested_datetime
        ]


        if len(matching_rows) == 0:

            raise HTTPException(
                status_code=404,
                detail="No historical record found for this date and time."
            )


        row = matching_rows.iloc[0]


        # ----------------------------------------------------
        # Prepare model data
        # ----------------------------------------------------

        prediction_data = data.copy()

        prediction_data = pd.get_dummies(
            prediction_data,

            columns=[
                "holiday",
                "weather_main",
                "weather_description"
            ]
        )


        # ----------------------------------------------------
        # Remove target and datetime
        # ----------------------------------------------------

        X = prediction_data.drop(
            columns=[
                "traffic_volume",
                "date_time"
            ]
        )


        # ----------------------------------------------------
        # Get requested row
        # ----------------------------------------------------

        row_index = matching_rows.index[0]

        X_row = X.loc[[row_index]]


        # ----------------------------------------------------
        # Match model features
        # ----------------------------------------------------

        model_features = model.feature_name_

        for feature in model_features:

            if feature not in X_row.columns:

                X_row[feature] = 0


        X_row = X_row[model_features]


        # ----------------------------------------------------
        # Predict
        # ----------------------------------------------------

        prediction = model.predict(X_row)[0]

        prediction = max(0, prediction)


        # ----------------------------------------------------
        # Actual value
        # ----------------------------------------------------

        actual = float(row["traffic_volume"])


        # ----------------------------------------------------
        # Prediction error
        # ----------------------------------------------------

        error = abs(actual - prediction)


        if actual != 0:

            error_percentage = (
                error / actual
            ) * 100

        else:

            error_percentage = 0


        # ----------------------------------------------------
        # Store prediction in Oracle
        # ----------------------------------------------------

        connection = None

        try:

            connection = get_oracle_connection()

            cursor = connection.cursor()


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
                    :date_time,
                    :actual,
                    :predicted
                )
                """,

                {
                    "date_time":
                        requested_datetime.to_pydatetime(),

                    "actual":
                        actual,

                    "predicted":
                        float(prediction)
                }
            )


            connection.commit()

            cursor.close()


            print(
                "Prediction stored in Oracle successfully."
            )


        except Exception as oracle_error:

            print(
                "Oracle insertion error:",
                oracle_error
            )


        finally:

            if connection is not None:

                connection.close()


        # ----------------------------------------------------
        # Traffic level
        # ----------------------------------------------------

        if prediction < 2500:

            traffic_status = "LOW"

        elif prediction < 4500:

            traffic_status = "MODERATE"

        else:

            traffic_status = "HIGH"


        # ----------------------------------------------------
        # Return result
        # ----------------------------------------------------

        return {

            "status": "success",

            "date_time":
                requested_datetime.strftime(
                    "%Y-%m-%d %H:%M"
                ),

            "actual":
                round(actual, 2),

            "predicted":
                round(float(prediction), 2),

            "error":
                round(error, 2),

            "error_percentage":
                round(error_percentage, 1),

            "traffic_status":
                traffic_status,

            "model":
                "LightGBM",

            "r2":
                0.9846
        }


    except HTTPException:

        raise


    except Exception as e:

        print("Prediction error:", e)

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


# ============================================================
# ORACLE ANALYTICS
# ============================================================

@app.get("/analytics")
def get_analytics():

    connection = None

    try:

        connection = get_oracle_connection()

        cursor = connection.cursor()


        # ----------------------------------------------------
        # Overall traffic statistics
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                ROUND(AVG(traffic_volume), 2),
                MIN(traffic_volume),
                MAX(traffic_volume)
            FROM TRAFFIC_DATA
            """
        )

        avg_traffic, min_traffic, max_traffic = cursor.fetchone()


        # ----------------------------------------------------
        # Busiest hour
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                hour,
                ROUND(AVG(traffic_volume), 2)
            FROM TRAFFIC_DATA
            GROUP BY hour
            ORDER BY AVG(traffic_volume) DESC
            FETCH FIRST 1 ROW ONLY
            """
        )

        busiest_hour, busiest_hour_average = cursor.fetchone()


        # ----------------------------------------------------
        # Weekday average
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                ROUND(AVG(traffic_volume), 2)
            FROM TRAFFIC_DATA
            WHERE is_weekend = 0
            """
        )

        weekday_average = cursor.fetchone()[0]


        # ----------------------------------------------------
        # Weekend average
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                ROUND(AVG(traffic_volume), 2)
            FROM TRAFFIC_DATA
            WHERE is_weekend = 1
            """
        )

        weekend_average = cursor.fetchone()[0]


        # ----------------------------------------------------
        # Model performance
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                model_name,
                test_mae,
                test_rmse,
                test_r2,
                training_time
            FROM MODEL_RESULTS
            ORDER BY test_rmse
            """
        )

        models = []


        for row in cursor.fetchall():

            models.append(
                {
                    "model": row[0],
                    "test_mae": float(row[1]),
                    "test_rmse": float(row[2]),
                    "test_r2": float(row[3]),
                    "training_time": float(row[4])
                }
            )


        cursor.close()

        connection.close()


        # ----------------------------------------------------
        # Return analytics
        # ----------------------------------------------------

        return {

            "status": "success",

            "traffic": {

                "average":
                    float(avg_traffic),

                "minimum":
                    int(min_traffic),

                "maximum":
                    int(max_traffic)
            },

            "busiest_hour": {

                "hour":
                    int(busiest_hour),

                "average":
                    float(busiest_hour_average)
            },

            "weekday_average":
                float(weekday_average),

            "weekend_average":
                float(weekend_average),

            "models":
                models
        }


    except Exception as e:

        if connection:

            connection.close()


        return {

            "status": "error",

            "message": str(e)
        }


# ============================================================
# PREDICTION HISTORY
# ============================================================

@app.get("/prediction-history")
def get_prediction_history():

    connection = None

    try:

        connection = get_oracle_connection()

        cursor = connection.cursor()

        # ----------------------------------------------------
        # Get latest unique predictions from Oracle
        # ----------------------------------------------------

        cursor.execute(
            """
            SELECT
                date_time,
                actual_traffic_volume,
                predicted_traffic_volume
            FROM
            (
                SELECT
                    date_time,
                    actual_traffic_volume,
                    predicted_traffic_volume,
                    ROW_NUMBER() OVER
                    (
                        PARTITION BY date_time
                        ORDER BY prediction_id DESC
                    ) AS row_number
                FROM TRAFFIC_PREDICTIONS
            )
            WHERE row_number = 1
            ORDER BY date_time DESC
            FETCH FIRST 10 ROWS ONLY
            """
        )

        rows = cursor.fetchall()

        predictions = []

        # ----------------------------------------------------
        # Process Oracle records
        # ----------------------------------------------------

        for row in rows:

            date_time = row[0]

            actual = float(row[1])

            predicted = float(row[2])

            error = abs(actual - predicted)

            if actual != 0:

                error_percentage = (
                    error / actual
                ) * 100

            else:

                error_percentage = 0

            # ------------------------------------------------
            # Traffic status
            # ------------------------------------------------

            if predicted < 2500:

                traffic_status = "LOW"

            elif predicted < 4500:

                traffic_status = "MODERATE"

            else:

                traffic_status = "HIGH"

            predictions.append(
                {
                    "date_time":
                        date_time.strftime(
                            "%Y-%m-%d %H:%M"
                        ),

                    "actual":
                        round(actual, 2),

                    "predicted":
                        round(predicted, 2),

                    "error":
                        round(error, 2),

                    "error_percentage":
                        round(error_percentage, 1),

                    "traffic_status":
                        traffic_status
                }
            )

        cursor.close()

        connection.close()

        # ----------------------------------------------------
        # Return history
        # ----------------------------------------------------

        return {

            "status": "success",

            "count":
                len(predictions),

            "predictions":
                predictions
        }

    except Exception as e:

        if connection:

            connection.close()

        print(
            "Prediction history error:",
            e
        )

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )