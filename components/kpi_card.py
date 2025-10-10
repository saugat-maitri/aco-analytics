import dash_bootstrap_components as dbc
from dash import html

from services.utils import calculate_change_metrics


def kpi_card(title, value, comparison_value, expected_value, comparison_id):
    comparison_percent, comparison_arrow, comparison_arrow_color = (
        calculate_change_metrics(value, comparison_value)
    )

    expected_changed, expected_arrow, expected_arrow_color = calculate_change_metrics(
        value, expected_value
    )

    is_utilization = comparison_id == "comparison-utilization"
    display_value = (
        f"{float(value):,.0f}" if is_utilization else f"${float(value):,.0f}"
    )
    comparison_display = (
        f"{float(comparison_value):,.0f}"
        if is_utilization
        else f"${float(comparison_value):,.0f}"
    )

    return dbc.Card(
        [
            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.H6(title, className="fw-semibold"),
                                    html.H1(
                                        display_value,
                                        className="my-2 fw-semibold",
                                        style={"font-size": "56px"},
                                    ),
                                    html.P(
                                        [
                                            html.Span(
                                                className="text-muted", id=comparison_id
                                            ),
                                            html.Span(": "),
                                            html.Span(
                                                comparison_display,
                                                className="fw-semibold",
                                            ),
                                        ],
                                        className="text-nowrap",
                                    ),
                                    html.P(
                                        [
                                            html.Span(
                                                "PMPM Expected: ",
                                                className="text-muted",
                                            ),
                                            html.Span(
                                                expected_value, className="fw-semibold"
                                            ),
                                        ],
                                        className="text-nowrap",
                                    ),
                                ],
                                width=7,
                            ),
                            dbc.Col(
                                [
                                    html.Div(
                                        [
                                            html.P(
                                                [
                                                    comparison_percent,
                                                    html.Span(
                                                        comparison_arrow,
                                                        className="ms-2",
                                                    ),
                                                ],
                                                className="fw-semibold",
                                                style={
                                                    "color": comparison_arrow_color,
                                                    "fontSize": "18px",
                                                },
                                            ),
                                            html.P(
                                                "vs comparison period",
                                                style={"fontSize": "14px"},
                                            ),
                                        ],
                                        className="mb-4 lh-sm",
                                    ),
                                    html.Div(
                                        [
                                            html.P(
                                                [
                                                    expected_changed,
                                                    html.Span(
                                                        expected_arrow, className="ms-2"
                                                    ),
                                                ],
                                                className="fw-semibold",
                                                style={
                                                    "color": expected_arrow_color,
                                                    "fontSize": "18px",
                                                },
                                            ),
                                            html.P(
                                                "vs expected",
                                                style={"fontSize": "14px"},
                                            ),
                                        ],
                                        className="lh-sm",
                                    ),
                                ],
                                width=5,
                                className="text-end",
                            ),
                        ]
                    ),
                ]
            )
        ]
    )
