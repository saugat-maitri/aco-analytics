import calendar
from datetime import date

import dash_bootstrap_components as dbc
from dash import dcc, html

from services.database import sqlite_manager


def header():
    query = "SELECT DISTINCT(YEAR_MONTH) FROM FACT_CLAIMS"
    claims_agg = sqlite_manager.query(query)

    # Use integer division to extract year from YEAR_MONTH which is in YYYYMM format
    years = sorted(((claims_agg["YEAR_MONTH"]).astype(int) // 100).unique())
    last_year = years[-1]
    last_month = 12
    last_day = calendar.monthrange(last_year, last_month)[1]
    return html.Div(
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
                className="my-1 header",
            )
