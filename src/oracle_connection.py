import oracledb
import os
from dotenv import load_dotenv

load_dotenv()

print("==============================")
print("ORACLE DATABASE CONNECTION")
print("==============================")

username = os.getenv("ORACLE_USER")
password = os.getenv("ORACLE_PASSWORD")
dsn = os.getenv("ORACLE_DSN", "localhost:1521/xe")

connection = oracledb.connect(
    user=username,
    password=password,
    dsn=dsn
)

print("\nOracle connection successful!")

cursor = connection.cursor()

cursor.execute("SELECT SYSDATE FROM dual")

result = cursor.fetchone()

print("Oracle server date and time:")
print(result[0])

cursor.close()
connection.close()

print("\nOracle connection closed.")