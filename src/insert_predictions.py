import pandas as pd
import oracledb

print("==============================")
print("INSERTING PREDICTIONS INTO ORACLE")
print("==============================")

# Load prediction CSV
data = pd.read_csv("outputs/traffic_predictions.csv")

print("\nPrediction data loaded!")
print("Number of records:", len(data))

# Oracle connection
username = "SYSTEM"
password = "chiman123"
dsn = "localhost:1521/xe"

connection = oracledb.connect(
    user=username,
    password=password,
    dsn=dsn
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