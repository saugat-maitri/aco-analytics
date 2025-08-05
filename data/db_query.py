import sqlite3
import pandas as pd
from constants import sqlite_path

def query_sqlite(sql_query: str) -> pd.DataFrame:
    conn = sqlite3.connect(sqlite_path)
    df = pd.read_sql_query(sql_query, conn)
    conn.close()
    return df
