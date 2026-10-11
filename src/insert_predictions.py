import pandas as pd
import oracledb
import os
from dotenv import load_dotenv

load_dotenv()

print("==============================")
print("INSERTING PREDICTIONS INTO ORACLE")
print("==============================")

# Load prediction CSV
data = pd.read_csv("outputs/traffic_predictions.csv")

print("\nPrediction data loaded!")
print("Number of records:", len(data))

# Oracle connection
ORACLE_USERNAME = os.getenv("ORACLE_USER")
ORACLE_PASSWORD = os.getenv("ORACLE_PASSWORD")
ORACLE_DSN = os.getenv("ORACLE_DSN", "localhost:1521/xe")

connection = oracledb.connect(
    user=ORACLE_USERNAME,
    password=ORACLE_PASSWORD,
    dsn=ORACLE_DSN
)

print("Oracle connection successful!")

cursor = connection.cursor()

# Insert query
sql = """
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
"""

# Insert records
for index, row in data.iterrows():

    cursor.execute(
        sql,
        (
            pd.to_datetime(row["date_time"]).to_pydatetime(),
            float(row["actual_traffic_volume"]),
            float(row["predicted_traffic_volume"])
        )
    )

# Save changes
connection.commit()

print("\nAll predictions inserted successfully!")

# Check number of records
cursor.execute("SELECT COUNT(*) FROM TRAFFIC_PREDICTIONS")

count = cursor.fetchone()[0]

print("Records in Oracle:", count)

cursor.close()
connection.close()

print("\nOracle connection closed.")