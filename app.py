import dash
import dash_bootstrap_components as dbc
from dash import html

from components.header import header
from services.database import sqlite_manager

sqlite_manager.initialize()

app = dash.Dash(
    __name__, 
    external_stylesheets=[dbc.themes.BOOTSTRAP], 
    suppress_callback_exceptions=True,
    assets_folder='assets',
    title="TUVA Health ACO Analytics",
    use_pages=True,
    pages_folder="reports"
)

app.layout = html.Div(
    [
        header(),
        dbc.Container(
            [dash.page_container], fluid=True
        ),
    ]
)

if __name__ == '__main__':
    app.run(debug=True)
