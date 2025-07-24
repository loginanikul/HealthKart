from sqlalchemy import create_engine,text
import pandas as pd
import matplotlib.pyplot as plt


# Replace with your MySQL username, password, and database name
username = 'root'           # Default MySQL user
password = 'Anikul@2143'  # Replace with your actual password
host = 'localhost'
port = '3306'               # Default MySQL port
database = 'Project'  # Replace with your database name

# SQLAlchemy MySQL connection string
engine = create_engine(
    f"mysql+pymysql://{username}:{password.replace('@', '%40')}@{host}:{port}/{database}"
)

# Executing a simple query
with engine.connect() as conn:
    df = pd.read_sql(text("SELECT * FROM Country"), conn)

    print(df)
x_col = df.columns[0]   # e.g., 'CountryName'
y_col = df.columns[1]

plt.figure(figsize=(12, 6))
for continent in df['continent'].unique():
    subset = df[df['continent'] == continent]
    plt.bar(subset['country_name'], subset['population'], label=continent)
    plt.xlabel("continet")   # e.g., 'Population' or 'GDP'


plt.title("Population by Country and Continent")
plt.xlabel("Country Name")
plt.ylabel("Population")
plt.xticks(rotation=45)
plt.legend(title="Continent")
plt.tight_layout()
plt.show()