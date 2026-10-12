import oracledb

print("==============================")
print("ORACLE DATABASE CONNECTION")
print("==============================")

username = "SYSTEM"
password = "chiman123"
dsn = "localhost:1521/xe"

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