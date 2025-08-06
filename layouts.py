from datetime import date
import calendar
import dash_bootstrap_components as dbc
from dash import html, dcc
import pandas as pd

from components import (
    pmpm_vs_expected_bar,
    cost_drivers_bar,
    demographics_card,
    risk_distribution_scatter
)

df = pd.read_csv('data/outlier_member_months.csv')

# Extract unique years and sort them
years = sorted(df['YEAR'].unique())
last_year = years[-1]
last_month = 12
last_day = calendar.monthrange(last_year, last_month)[1]

def create_layout():
    return dbc.Container([
        html.Div([
            html.Div([
                html.Img(src="assets/tuva_health_logo.png", width=220, className="me-2"),
                html.H3("| ACO Analytics", style={"color": "#1e7baa", "font-size": "24px"})
            ], className="d-flex align-items-center"),
            html.Div([
                dbc.Stack([
                    html.Div([
                        html.P("Selected Period", className="mb-1 fw-semibold text-teal-blue", style={"font-size": "12px"}),
                        dcc.DatePickerRange(
                            id='my-date-picker-range',
                            min_date_allowed=date(years[0], 1, 1),
                            max_date_allowed=date(last_year, last_month, last_day),
                            initial_visible_month=date(last_year, 1, 1),
                            end_date=date(last_year, last_month, last_day),
                            start_date=date(last_year, 1, 1),
                            style={"width": "195px"}
                        ),
                    ], style={"flex": 1}),
                    html.Div([
                        html.P("Comparison Period", className="mb-1 fw-semibold text-teal-blue", style={"font-size": "12px"}),
                        dcc.Dropdown(
                            value="Same Period Last Year",
                            id='comparison-period-dropdown',
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
                            style={"width": "195px"}
                        )
                    ], style={"flex": "auto"}),
                ], direction="horizontal", gap=2, style={"alignItems": "stretch"}),
            ], className="my-2"),
        ], className="d-flex justify-content-between my-1"),
        html.Div([
            dbc.Row([
                dbc.Col(id="pmpm-cost-card", width=4),
                dbc.Col(id="utilization-card", width=4),
                dbc.Col(id="cost-per-encounter-card", width=4),
            ], className="mb-4"),

            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("PMPM Performance vs Expected by Encounter Group", className="mb-2 text-teal-blue"),
                            dcc.Graph(id='pmpm-performance', figure=pmpm_vs_expected_bar(), style={"height": "270px"})
                        ])
                    ])
                ], width=8),

                dbc.Col([
                    dbc.Stack([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("PMPM Trend", className="text-teal-blue"),
                                dcc.Graph(id='pmpm-trend')
                            ])
                        ]),
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("PKPY Trend", className="text-teal-blue"),
                                dcc.Graph(id='pkpy-trend')
                            ])
                        ]),
                    ], gap=2)
                ], width=4),
            ]),
            dbc.Row([
                dbc.Col([
                    dbc.Card([
                        dbc.CardBody([
                            html.H5("Cost Drivers Analysis", className="text-teal-blue"),
                            dbc.Tabs([
                                dbc.Tab(dcc.Graph(id='cost-drivers-graph', figure=cost_drivers_bar()), label="Encounter Type"),
                                dbc.Tab(
                                    html.Div(
                                        id="condition-ccsr",
                                    ),
                                    label="Condition (CCSR)"
                                ),
                                dbc.Tab(label="Provider Specialty"),                            ])
                        ])
                    ])
                ], width=8),

                dbc.Col([
                    dbc.Stack([
                        dbc.Card([
                            dbc.CardBody([
                                html.H5("Cost Per Trend", className="text-teal-blue"),
                                dcc.Graph(id='cost-per-trend')
                            ])
                        ]),
                        dbc.Stack([
                            demographics_card(),
                            dbc.Card([
                                dbc.CardBody([
                                    html.H5("Risk Distribution", className="text-teal-blue text-nowrap"),
                                    dcc.Graph(id='risk-distribution', figure=risk_distribution_scatter())
                                ])
                            ], className="h-100", style={"flex": "1"}),
                        ], direction="horizontal", gap=2, style={"alignItems": "stretch"})
                    ], gap=2)
                ], width=4),
            ], className="mt-4")
        ], className="bg-light-subtle")
    ], fluid=True)
