import dash
import dash_bootstrap_components as dbc

from data.data_loader import initialize_sqlite
from layouts import create_layout
from constants import sqlite_path
import callbacks  # Import callbacks to register them with the app

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP], suppress_callback_exceptions=True)
app.title = "TUVA Health ACO Analytics"

# Initialize SQLite database connection on startup
initialize_sqlite(sqlite_path)  # Initialize SQLite database with Snowflake data
app.layout = create_layout()

if __name__ == '__main__':
    app.run(debug=False)
