import dash_bootstrap_components as dbc
from dash import dcc, html, register_page

from .callbacks import *

register_page(
    module=__name__,
    path='/',
    name='Tuva Dash App',
    title='Tuva Dash App'
)

layout = dbc.Container(
        [
            html.Div(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    dbc.Row([
                                        dbc.Col(id="pmpm-cost-card", width=6, className="mb-3"),
                                        dbc.Col(id="demographic-card", width=6, className="mb-3"),
                                    ]),
                                    dbc.Card(
                                        [
                                            dbc.CardBody(
                                                [
                                                    html.H5(
                                                        "PMPM Performance vs Expected by Encounter Group",
                                                        className="mb-2 text-teal-blue",
                                                    ),
                                                    dcc.Graph(
                                                        id="encounter-group-chart",
                                                        style={"height": "270px"},
                                                    ),
                                                ]
                                            )
                                        ],
                                        className="mb-3"
                                    ),
                                    dbc.Card(
                                        [
                                            dbc.CardBody(
                                                [
                                                    html.H5(
                                                        "Cost Drivers Analysis",
                                                        className="text-teal-blue",
                                                    ),
                                                    dbc.Tabs(
                                                        [
                                                            dbc.Tab(
                                                                html.Div(
                                                                    dcc.Graph(
                                                                        id="encounter-type-chart",
                                                                    ),
                                                                    style={
                                                                        "overflowY": "auto",
                                                                        "maxHeight": "400px",
                                                                    },
                                                                ),
                                                                label="Encounter Type",
                                                            ),
                                                            dbc.Tab(
                                                                html.Div(
                                                                    dcc.Graph(
                                                                        id="condition-ccsr-chart",
                                                                    ),
                                                                    style={
                                                                        "overflowY": "auto",
                                                                        "maxHeight": "400px",
                                                                    },
                                                                ),
                                                                label="Condition (CCSR)",
                                                            ),
                                                            dbc.Tab(
                                                                html.Div(
                                                                    dcc.Graph(
                                                                        id="provider-specialty-bar",
                                                                    ),
                                                                    style={
                                                                        "overflowY": "auto",
                                                                        "maxHeight": "400px",
                                                                    },
                                                                ),
                                                                label="Provider Specialty",
                                                            ),
                                                        ]
                                                    ),
                                                ]
                                            )
                                        ]
                                    ),
                                ],
                                width=8,
                            ),
                            dbc.Col(
                                [
                                    dbc.Card(
                                        dbc.CardBody(
                                            [
                                                html.H5(
                                                    "Risk Distribution",
                                                    className="text-teal-blue text-nowrap",
                                                ),
                                                dcc.Graph(
                                                    id="risk-distribution-card",
                                                ),
                                            ]
                                        ),
                                        className="mb-3"
                                    ),
                                    dbc.Stack(
                                        [
                                            dbc.Card(
                                                [
                                                    dbc.CardBody(
                                                        [
                                                            html.H5(
                                                                "PMPM Trend",
                                                                className="text-teal-blue",
                                                            ),
                                                            dcc.Graph(id="pmpm-trend"),
                                                        ]
                                                    )
                                                ]
                                            ),
                                            dbc.Card(
                                                [
                                                    dbc.CardBody(
                                                        [
                                                            html.H5(
                                                                "PKPY Trend",
                                                                className="text-teal-blue",
                                                            ),
                                                            dcc.Graph(id="pkpy-trend"),
                                                        ]
                                                    )
                                                ]
                                            ),
                                            dbc.Card(
                                                [
                                                    dbc.CardBody(
                                                        [
                                                            html.H5(
                                                                "Cost Per Trend",
                                                                className="text-teal-blue",
                                                            ),
                                                            dcc.Graph(
                                                                id="cost-per-trend"
                                                            ),
                                                        ]
                                                    )
                                                ]
                                            ),
                                        ],
                                        gap=2,
                                    )
                                ],
                                width=4,
                            ),
                        ],
                        className="mt-4",
                    ),
                ],
                className="bg-light-subtle",
            ),
        ],
        fluid=True,
    )