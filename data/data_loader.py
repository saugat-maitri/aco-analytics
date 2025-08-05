import sqlite3
from .db_manager import get_snowflake_connection
from constants import table_list

def initialize_sqlite(db_path: str):
    """Initialize SQLite database with data from Snowflake."""
    # Get Snowflake connection using the centralized connection manager
    print("Initializing SQLite database with Snowflake data...")
    snowflake_conn = get_snowflake_connection()

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
            sqlite_conn = sqlite3.connect(db_path)
            df.to_sql(table_name, sqlite_conn, if_exists='replace', index=False)
            sqlite_conn.close()
            
            print(f"Successfully loaded {len(df)} records into {table_name}")
            
        except Exception as e:
            print(f"Error loading table {table_name}: {e}")
            continue
        finally:
            if 'cursor' in locals():
                cursor.close()
    
    print(f"SQLite database initialization completed: {db_path}")
