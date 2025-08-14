from datetime import date
import calendar
import dash_bootstrap_components as dbc
from dash import html, dcc
from utils import load_data

def create_layout():
    claims_agg, _ = load_data()

    # Use integer division to extract year from YEAR_MONTH which is in YYYYMM format
    years = sorted((claims_agg["YEAR_MONTH"] // 100).unique())
    last_year = years[-1]
    last_month = 12
    last_day = calendar.monthrange(last_year, last_month)[1]

    return dbc.Container(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Img(
                                src="assets/tuva_health_logo.png",
                                width=220,
                                className="me-2",
                            ),
                            html.H3(
                                "| ACO Analytics",
                                style={"color": "#1e7baa", "font-size": "24px"},
                            ),
                        ],
                        className="d-flex align-items-center",
                    ),
                    html.Div(
                        [
                            dbc.Stack(
                                [
                                    html.Div(
                                        [
                                            html.P(
                                                "Selected Period",
                                                className="mb-1 fw-semibold text-teal-blue",
                                                style={"font-size": "12px"},
                                            ),
                                            dcc.DatePickerRange(
                                                id="date-picker-input",
                                                min_date_allowed=date(years[0], 1, 1),
                                                max_date_allowed=date(
                                                    last_year, last_month, last_day
                                                ),
                                                end_date=date(
                                                    last_year, last_month, last_day
                                                ),
                                                start_date=date(last_year, 1, 1),
                                                style={"width": "195px"},
                                            ),
                                        ],
                                        style={"flex": 1},
                                    ),
                                    html.Div(
                                        [
                                            html.P(
                                                "Comparison Period",
                                                className="mb-1 fw-semibold text-teal-blue",
                                                style={"font-size": "12px"},
                                            ),
                                            dcc.Dropdown(
                                                value="Same Period Last Year",
                                                id="comparison-period-dropdown",
                                                options=[
                                                    "Previous 18 Months",
                                                    "Previous Month",
                                                    "Previous Period",
                                                    "Previous Quarter",
                                                    "Previous Year",
                                                    "Same Period Last Year",
                                                ],
                                                placeholder="Select a comparison period",
                                                clearable=False,
                                                style={"width": "195px"},
                                            ),
                                        ],
                                        style={"flex": "auto"},
                                    ),
                                ],
                                direction="horizontal",
                                gap=2,
                                style={"alignItems": "stretch"},
                            ),
                        ],
                        className="my-2",
                    ),
                ],
                className="my-1 top-bar",
            ),
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
                                                        id="pmpm-performance",
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
                                                                        id="encounter-type-bar",
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
                                                                        id="condition-ccsr-cost-driver",
                                                                    ),
                                                                    style={
                                                                        "overflowY": "auto",
                                                                        "maxHeight": "400px",
                                                                    },
                                                                ),
                                                                label="Condition CCSR Cost Driver",
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
