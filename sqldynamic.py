import json
import mysql.connector
from decimal import Decimal

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

# 🔹 Dynamic connection inputs
host = input("Enter MySQL host: ")
user = input("Enter MySQL username: ")
password = input("Enter MySQL password: ")
database = input("Enter database name: ")

# 🔹 Connect dynamically
conn = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=database
)

cursor = conn.cursor(dictionary=True)
cursor.execute("SELECT city, house_size, price, zip_code, Status FROM project.realtor_data")

rows = cursor.fetchall()
json_data = json.dumps(rows, indent=4, default=decimal_default)

with open('realtor_data.json', 'w') as f:
    f.write(json_data)

print("✅ Data exported successfully to realtor_data.json")