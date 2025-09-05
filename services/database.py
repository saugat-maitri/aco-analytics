import os
import sqlite3
from pathlib import Path
from typing import Optional

import pandas as pd
import snowflake.connector
from dotenv import load_dotenv
from flask import abort

from services.queries import sqlite_path, table_list


class SnowflakeManager:
    """Manages connection to Snowflake."""

    _connection: Optional[snowflake.connector.connection.SnowflakeConnection] = None

    def __init__(self):
        load_dotenv()
        self.config = {
            "user": os.getenv("SNOWFLAKE_USER"),
            "password": os.getenv("SNOWFLAKE_PASSWORD"),
            "account": os.getenv("SNOWFLAKE_ACCOUNT"),
            "warehouse": os.getenv("SNOWFLAKE_WAREHOUSE"),
            "database": os.getenv("SNOWFLAKE_DATABASE"),
            "schema": os.getenv("SNOWFLAKE_SCHEMA"),
            "auth_method": os.getenv("SNOWFLAKE_AUTH_METHOD"),
        }

    def get_connection(self):
        """Return a singleton Snowflake connection."""
        if SnowflakeManager._connection is None:
            try:
                connect_args = {
                    "user": self.config["user"],
                    "account": self.config["account"],
                    "warehouse": self.config["warehouse"],
                    "database": self.config["database"],
                    "schema": self.config["schema"],
                    "autocommit": True,
                    "client_session_keep_alive": True,
                }

                if self.config.get("auth_method", "").lower() == "externalbrowser":
                    connect_args["authenticator"] = "externalbrowser"
                else:
                    connect_args["password"] = self.config["password"]

                SnowflakeManager._connection = snowflake.connector.connect(
                    **connect_args
                )
                print("Snowflake connection established successfully")

            except snowflake.connector.Error as e:
                print(f"❌ Error connecting to Snowflake: {e}")
                abort(500, description="Error connecting to Snowflake")

        return SnowflakeManager._connection

    def close(self):
        """Close the Snowflake connection if open."""
        if SnowflakeManager._connection:
            SnowflakeManager._connection.close()
            SnowflakeManager._connection = None
            print("Snowflake connection closed")


class SQLiteManager:
    """Handles SQLite queries and initialization from CSV or Snowflake."""

    def __init__(self, db_path: str = sqlite_path):
        self.db_path = db_path

    def query(self, sql_query: str) -> pd.DataFrame:
        """Run a SQL query against the SQLite database."""
        conn = sqlite3.connect(self.db_path)
        try:
            return pd.read_sql_query(sql_query, conn)
        finally:
            conn.close()

    def _load_from_csv(self, conn: sqlite3.Connection, csv_folder: str):
        """Load data from CSV files into SQLite."""
        print("Loading data from CSV files...")
        csv_path = Path(csv_folder)

        for table_info in table_list:
            table_name = table_info["table_name"]
            csv_file = csv_path / f"{table_name}.csv"

            if not csv_file.exists():
                raise FileNotFoundError(
                    f"❌ Required CSV file missing for {table_name}: {csv_file}"
                )

            try:
                df = pd.read_csv(csv_file)
                df.to_sql(table_name, conn, if_exists="replace", index=False)
                print(f"{len(df)} records loaded into {table_name} from CSV")
            except Exception as e:
                raise RuntimeError(f"❌ Error loading {table_name} from CSV: {e}")

    def _load_from_snowflake(
        self, conn: sqlite3.Connection, sf_manager: SnowflakeManager
    ):
        """Load data from Snowflake into SQLite."""
        sf_conn = sf_manager.get_connection()

        try:
            for table_info in table_list:
                table_name = table_info["table_name"]
                query = table_info["query"]

                try:
                    print(f"Loading {table_name} from Snowflake...")
                    cursor = sf_conn.cursor()
                    cursor.execute(query)
                    df = cursor.fetch_pandas_all()
                    df.to_sql(table_name, conn, if_exists="replace", index=False)
                    print(f"{len(df)} records loaded into {table_name} from Snowflake")
                except Exception as e:
                    print(f"❌ Error loading {table_name} from Snowflake: {e}")
                finally:
                    cursor.close()
        finally:
            sf_manager.close()

    def initialize(self):
        """Initialize SQLite database.

        - If `.env` exists → load from Snowflake
        - Otherwise → load from CSV files.
        """
        conn = sqlite3.connect(self.db_path)
        env_file = Path(__file__).resolve().parents[1] / ".env"
        try:
            if env_file.exists():
                print("Using Snowflake as data source...")
                sf_manager = SnowflakeManager()
                self._load_from_snowflake(conn, sf_manager)
            else:
                print("Using CSV as data source...")
                csv_folder = Path(__file__).resolve().parents[1] / "csv_sample"
                self._load_from_csv(conn, str(csv_folder))
        finally:
            conn.close()

        print(f"SQLite initialization complete: {self.db_path}")


sqlite_manager = SQLiteManager()
