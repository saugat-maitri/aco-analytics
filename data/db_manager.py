import os

import snowflake.connector
from dotenv import load_dotenv
from flask import abort

# Load environment variables from .env
load_dotenv()

# Global connection instance
_snowflake_connection = None

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

def get_snowflake_connection():
    """Get or create a Snowflake connection (singleton pattern)."""
    global _snowflake_connection
    
    if _snowflake_connection is None:
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
                
            _snowflake_connection = snowflake.connector.connect(**connect_args)
            print("Snowflake connection established successfully")
            
        except snowflake.connector.Error as e:
            print(f"Error connecting to Snowflake: {e}")
            abort(500, description="Error connecting to Snowflake")
    
    return _snowflake_connection
