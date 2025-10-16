import dash_bootstrap_components as dbc
from dash import dcc, html, register_page

from .callbacks import *

register_page(
    module=__name__,
    path="/condition-ccsr",
    name="Tuva Dash App-Condition CCSR",
    title="Tuva Dash App-Condition CCSR",
)


layout = (
    html.Div(
        [
            dbc.Row(
                [
                    dbc.Col(
                        dbc.Stack(
                            id="ccsr-metrics-container",
                            children=[],
                            gap=3,
                        ),
                        width=2,
                    ),
                    dbc.Col(
                        [
                            dbc.Stack(
                                [
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                dbc.Card(
                                                    [
                                                        dbc.CardBody(
                                                            [
                                                                html.H5(
                                                                    "PMPM by Encounter Group (vs Expected)",
                                                                    className="mb-2 text-teal-blue",
                                                                    style={
                                                                        "text-wrap": "nowrap"
                                                                    },
                                                                ),
                                                                dcc.Graph(
                                                                    id="ccsr-encounter-group-chart",
                                                                    style={
                                                                        "height": "250px"
                                                                    },
                                                                ),
                                                            ],
                                                        )
                                                    ],
                                                ),
                                                width=6,
                                            ),
                                            dbc.Col(
                                                dbc.Card(
                                                    [
                                                        dbc.CardBody(
                                                            [
                                                                html.H5(
                                                                    "PMPM by Encounter Type",
                                                                    className="mb-2 text-teal-blue",
                                                                ),
                                                                dcc.Graph(
                                                                    id="ccsr-encounter-type-chart",
                                                                    style={
                                                                        "overflowY": "auto",
                                                                        "height": "250px",
                                                                    },
                                                                ),
                                                            ],
                                                        )
                                                    ],
                                                ),
                                                width=6,
                                            ),
                                        ]
                                    ),
                                    dbc.Row(
                                        [
                                            dbc.Col(
                                                dbc.Card(
                                                    [
                                                        html.H5(
                                                            "Paid Amount by Primary Diagnosis",
                                                            className="m-3 text-teal-blue",
                                                        ),
                                                        dbc.CardBody(
                                                            [
                                                                dcc.Graph(
                                                                    id="ccsr-paid-by-diagnosis-chart",
                                                                ),
                                                            ],
                                                            style={"height": "300px"},
                                                            className="mb-3",
                                                        ),
                                                    ]
                                                ),
                                                width=6,
                                            ),
                                            dbc.Col(
                                                dbc.Card(
                                                    [
                                                        html.H5(
                                                            "Cost Per by Facility",
                                                            className="m-3 text-teal-blue",
                                                        ),
                                                        dbc.CardBody(
                                                            [
                                                                dcc.Graph(
                                                                    id="ccsr-cost-per-by-facility-chart",
                                                                ),
                                                            ],
                                                            style={
                                                                "overflowY": "auto",
                                                                "maxHeight": "300px",
                                                            },
                                                            className="mb-3",
                                                        ),
                                                    ]
                                                ),
                                                width=6,
                                            ),
                                        ],
                                    ),
                                ],
                                gap=3,
                            )
                        ],
                        width=10,
                    ),
                ],
                className="mt-4",
            ),
        ],
        className="bg-light-subtle",
    ),
)
