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
    df = pd.read_sql(text("SELECT * FROM influencers"), conn)
    print(df)
