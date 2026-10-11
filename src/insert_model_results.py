import oracledb
import os
from dotenv import load_dotenv

load_dotenv()

print("==============================")
print("INSERTING MODEL RESULTS")
print("==============================")

# Oracle connection
ORACLE_USERNAME = os.getenv("ORACLE_USER")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD")
ORACLE_DSN = os.getenv("ORACLE_DSN", "localhost:1521/xe")

connection = oracledb.connect(
    user=ORACLE_USERNAME,
    password=ORACLE_PASSWORD,
    dsn=ORACLE_DSN
)

print("\nOracle connection successful!")

cursor = connection.cursor()

# LightGBM results
cursor.execute("""
    INSERT INTO MODEL_RESULTS
    (
        model_name,
        train_mae,
        test_mae,
        train_rmse,
        test_rmse,
        train_r2,
        test_r2,
        training_time
    )
    VALUES
    (
        :1, :2, :3, :4, :5, :6, :7, :8
    )
""", (
    "LightGBM",
    158.45,
    156.71,
    253.81,
    244.83,
    0.9837,
    0.9846,
    2.30
))

# XGBoost results
cursor.execute("""
    INSERT INTO MODEL_RESULTS
    (
        model_name,
        train_mae,
        test_mae,
        train_rmse,
        test_rmse,
        train_r2,
        test_r2,
        training_time
    )
    VALUES
    (
        :1, :2, :3, :4, :5, :6, :7, :8
    )
""", (
    "XGBoost",
    150.05,
    155.01,
    237.20,
    246.22,
    0.9858,
    0.9844,
    3.48
))

# Save changes
connection.commit()

print("\nModel results inserted successfully!")

# Check records
cursor.execute("SELECT COUNT(*) FROM MODEL_RESULTS")

count = cursor.fetchone()[0]

print("Model result records in Oracle:", count)

cursor.close()
connection.close()

print("\nOracle connection closed.")