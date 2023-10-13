import os
import sqlite3
import pandas as pd
from dotenv import load_dotenv


# Load environment variables from the .env file
load_dotenv()

# Path of SQLite database
db_path = os.getenv("DB_PATH")

# Function to create all the required tables


def create_tables():
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()

    # Create a table to store observational data for stores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS store_data (
            store_id INT,
            timestamp_utc TIMESTAMP,
            status VARCHAR(10)
        )
    """)

    # Create a table to store business hours for stores
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS business_hours (
            store_id INT,
            day_of_week INT,
            start_time_local TIME,
            end_time_local TIME
        )
    """)

    # Create a table to store store timezones
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS store_timezones (
            store_id INT,
            timezone_str VARCHAR(50)
        )
    """)
    connection.commit()
    connection.close()


def import_data():
    connection = sqlite3.connect(db_path)
    data_directory = os.path.join(os.path.dirname(__file__), "data")
    # Read CSV files and store them in the SQLite database
    store_data_df = pd.read_csv(os.path.join(data_directory, "store_data.csv"))
    store_data_df.to_sql('store_data', connection,
                         if_exists='replace', index=False)

    business_hours_df = pd.read_csv(
        os.path.join(data_directory, "business_hours.csv"))
    business_hours_df.to_sql('business_hours', connection,
                             if_exists='replace', index=False)

    store_timezones_df = pd.read_csv(
        os.path.join(data_directory, "store_timezones.csv"))
    store_timezones_df.to_sql('store_timezones', connection,
                              if_exists='replace', index=False)
    connection.close()


def retrieve_data():
    connection = sqlite3.connect(db_path)
    # Retrieve all the necessary data from DB into a pandas dataframe
    store_data_df = pd.read_sql_query("SELECT * FROM store_data", connection)
    business_hours_df = pd.read_sql_query(
        "SELECT * FROM business_hours", connection)
    store_timezones_df = pd.read_sql_query(
        "SELECT * FROM store_timezones", connection)
    connection.close()
    return (store_data_df, business_hours_df, store_timezones_df)
