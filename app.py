from urllib.parse import parse_qs, urlparse

import dash
import dash_bootstrap_components as dbc
from dash import Input, Output, callback, dcc, html

from components.header import header
from services.database import sqlite_manager

sqlite_manager.initialize()

app = dash.Dash(
    __name__,
    external_stylesheets=[dbc.themes.BOOTSTRAP],
    suppress_callback_exceptions=True,
    assets_folder="assets",
    title="Tuva Health Cost and Utilization",
    use_pages=True,
    pages_folder="reports",
)

app.layout = html.Div(
    [
        dcc.Location(id="url", refresh="callback-nav"),
        header(),
        dbc.Container([dash.page_container], fluid=True),
    ]
)


@callback(
    Output("drillthrough-title", "children"),
    Input("url", "href"),
)
def update_drillthrough_title(href):
    if not href:
        return ""

    parsed = urlparse(href)
    query = parse_qs(parsed.query)
    path = parsed.path

    if path == "/condition-ccsr":
        return query.get("ccsr", [""])[0]
    else:
        return path.replace("/", "").replace("%20", " ")


if __name__ == "__main__":
    app.run(debug=True)
