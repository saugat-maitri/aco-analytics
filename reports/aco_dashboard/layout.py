import dash_bootstrap_components as dbc
from dash import dcc, html, register_page

from .callbacks import *

register_page(module=__name__, path="/", name="Tuva Dash App", title="Tuva Dash App")

layout = (
    html.Div(
        dbc.Row(
            [
                dbc.Col(
                    dbc.Stack(
                        [
                            dbc.Col(
                                id="pmpm-cost-card",
                                width=12,
                                className="w-100",
                            ),
                            dbc.Card(
                                dbc.CardBody(
                                    [
                                        html.H5(
                                            "PMPM Trend",
                                            className="text-teal-blue",
                                        ),
                                        dcc.Graph(id="pmpm-trend"),
                                    ]
                                ),
                            ),
                            dbc.Col(
                                id="demographic-card",
                                width=12,
                                className="w-100",
                            ),
                        ],
                        gap=3,
                    ),
                    width=4,
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
                                                            ),
                                                            dcc.Graph(
                                                                id="encounter-group-chart",
                                                            ),
                                                        ],
                                                        className="p-2",
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
                                                                "Total Paid by Cohort",
                                                                className="mb-2 text-teal-blue",
                                                            ),
                                                            dcc.Graph(
                                                                id="paid-by-cohort-chart",
                                                            ),
                                                        ],
                                                        className="p-2",
                                                    )
                                                ],
                                            ),
                                            width=6,
                                        ),
                                    ]
                                ),
                                dbc.Card(
                                    dbc.CardBody(
                                        [
                                            html.H5(
                                                "PMPM By Encounter Group",
                                                className="mb-2 text-teal-blue",
                                            ),
                                            dcc.Graph(
                                                id="encounter-group-percentage-chart",
                                            ),
                                        ]
                                    )
                                ),
                                dbc.Card(
                                    dbc.CardBody(
                                        [
                                            html.H5(
                                                "PMPM By CCSR Category (vs Comparison Period)",
                                                className="mb-2 text-teal-blue",
                                            ),
                                            dcc.Graph(
                                                id="condition-ccsr-chart",
                                            ),
                                        ],
                                        style={
                                            "overflowY": "auto",
                                            "maxHeight": "400px",
                                        },
                                    )
                                ),
                            ],
                            gap=3,
                        )
                    ],
                    width=8,
                ),
            ],
            className="mt-4",
        ),
        className="bg-light-subtle",
    ),
)
