import os
from flask import abort
import snowflake.connector
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

snowflake_pool = None

# Setup Snowflake connection parameters
SNOWFLAKE_CONFIG = {
    "user": os.getenv("SNOWFLAKE_USER"),
    "password": os.getenv("SNOWFLAKE_PASSWORD"),
    "account": os.getenv("SNOWFLAKE_ACCOUNT"),
    "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
    "database": os.getenv("SNOWFLAKE_DATABASE"),
    "schema": os.getenv("SNOWFLAKE_SCHEMA"),
    "auth_method": os.getenv("SNOWFLAKE_AUTH_METHOD")
}

def connect_snowflake():
    global snowflake_pool
    if snowflake_pool is None:
        try:
            connect_args = {
                "user": SNOWFLAKE_CONFIG["user"],
                "account": SNOWFLAKE_CONFIG["account"],
                "warehouse": SNOWFLAKE_CONFIG["warehouse"],
                "database": SNOWFLAKE_CONFIG["database"],
                "schema": SNOWFLAKE_CONFIG["schema"],
                "autocommit": True,
                "client_session_keep_alive": True
            }
            if SNOWFLAKE_CONFIG.get("auth_method", "").lower() == "externalbrowser":
                connect_args["authenticator"] = "externalbrowser"
            else:
                connect_args["password"] = SNOWFLAKE_CONFIG["password"]
            snowflake_pool = snowflake.connector.connect(**connect_args)
        except snowflake.connector.Error as e:
            print(f"Error connecting to Snowflake: {e}")
            abort(500, description="Error connecting to Snowflake")
    return snowflake_pool

def fetch_data(query):
    conn = connect_snowflake()
    try:
        cursor = conn.cursor()
        # Ensure query is optimized, avoiding `SELECT *`
        cursor.execute(query)
        data = cursor.fetch_pandas_all()
        return data
    except snowflake.connector.Error as e:
        print(f"Error executing query: {e}")
        abort(500, description="Error executing Snowflake query")
    finally:
        cursor.close()