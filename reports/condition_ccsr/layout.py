from dash import html, register_page

register_page(
    module=__name__,
    path="/condition-ccsr",
    name="Tuva Dash App-Condition CCSR",
    title="Tuva Dash App-Condition CCSR",
)


layout = (
    html.Div(
        "Condition CCSR",
        className="bg-light-subtle",
    ),
)
