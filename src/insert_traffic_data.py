import pandas as pd
import oracledb

print("==============================")
print("INSERTING TRAFFIC DATA INTO ORACLE")
print("==============================")

# Load processed traffic data
data = pd.read_csv("outputs/processed_traffic_data.csv")

print("\nProcessed traffic data loaded!")
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
    INSERT INTO TRAFFIC_DATA
    (
        date_time,
        traffic_volume,
        temp,
        rain_1h,
        snow_1h,
        clouds_all,
        holiday,
        weather_main,
        weather_description,
        year,
        month,
        day,
        hour,
        day_of_week,
        is_weekend,
        is_peak_hour,
        traffic_lag_1h,
        traffic_lag_2h,
        traffic_lag_24h,
        traffic_lag_168h
    )
    VALUES
    (
        :1, :2, :3, :4, :5, :6, :7, :8, :9, :10,
        :11, :12, :13, :14, :15, :16, :17, :18, :19, :20
    )
"""

# Insert each record
for index, row in data.iterrows():

    cursor.execute(
        sql,
        (
            pd.to_datetime(row["date_time"]).to_pydatetime(),
            float(row["traffic_volume"]),
            float(row["temp"]),
            float(row["rain_1h"]),
            float(row["snow_1h"]),
            float(row["clouds_all"]),
            str(row["holiday"]),
            str(row["weather_main"]),
            str(row["weather_description"]),
            int(row["year"]),
            int(row["month"]),
            int(row["day"]),
            int(row["hour"]),
            int(row["day_of_week"]),
            int(row["is_weekend"]),
            int(row["is_peak_hour"]),
            float(row["traffic_lag_1h"]),
            float(row["traffic_lag_2h"]),
            float(row["traffic_lag_24h"]),
            float(row["traffic_lag_168h"])
        )
    )

# Save changes
connection.commit()

print("\nAll traffic data inserted successfully!")

# Check number of records
cursor.execute("SELECT COUNT(*) FROM TRAFFIC_DATA")

count = cursor.fetchone()[0]

print("Records in Oracle:", count)

cursor.close()
connection.close()

print("\nOracle connection closed.")