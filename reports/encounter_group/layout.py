from dash import html, register_page

# from .callbacks import *

register_page(
    module=__name__,
    path="/encounter-group",
    name="Tuva Dash App-Encounter Group",
    title="Tuva Dash App-Encounter Group",
)


layout = (
    html.Div(
        "Encounter Group",
        className="bg-light-subtle",
    ),
)
