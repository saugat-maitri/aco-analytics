import sqlite3
import os
import pandas as pd
from pathlib import Path
from .db_manager import get_snowflake_connection
from constants import table_list

def load_from_csv(sqlite_conn: sqlite3.Connection, csv_folder: str):
    """Load data from CSV files into SQLite database."""
    print("Loading data from CSV files...")
    csv_path = Path(csv_folder)
    
    for table_info in table_list:
        table_name = table_info["table_name"]
        csv_file = csv_path / f"{table_name}.csv"
        
        if csv_file.exists():
            try:
                df = pd.read_csv(csv_file)
                df.to_sql(table_name, sqlite_conn, if_exists='replace', index=False)
                print(f"Successfully loaded {len(df)} records from CSV into {table_name}")
            except Exception as e:
                print(f"Error loading CSV for {table_name}: {e}")
        else:
            print(f"CSV file not found for {table_name}: {csv_file}")

def initialize_sqlite(db_path: str):
    """Initialize SQLite database with data from either Snowflake or CSV files."""
    print("Checking data source configuration...")
    env_file_exists = os.path.exists(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env'))
    
    sqlite_conn = sqlite3.connect(db_path)

    if env_file_exists:
        print("Found .env file, initializing SQLite database with Snowflake data...")
        snowflake_conn = get_snowflake_connection()

    try:
        if env_file_exists:
            try:
                for table_info in table_list:
                    print(f"Loading table: {table_info['table_name']} from Snowflake to SQLite")
                    query = table_info["query"]
                    table_name = table_info["table_name"]
                    
                    try:
                        # Fetch data from Snowflake
                        cursor = snowflake_conn.cursor()
                        cursor.execute(query)
                        df = cursor.fetch_pandas_all()
                        
                        # Store to SQLite
                        df.to_sql(table_name, sqlite_conn, if_exists='replace', index=False)
                        
                        print(f"Successfully loaded {len(df)} records into {table_name}")
                        
                    except Exception as e:
                        print(f"Error loading table {table_name} from Snowflake: {e}")
                        continue
                    finally:
                        if cursor is not None:
                            cursor.close()
            finally:
                if snowflake_conn is not None:
                    snowflake_conn.close()
        else:
            # Load from CSV files if .env doesn't exist
            csv_folder = os.path.join(os.path.dirname(__file__), 'csv_sample')
            load_from_csv(sqlite_conn, csv_folder)
    finally:
        sqlite_conn.close()
    
    print(f"SQLite database initialization completed: {db_path}")
