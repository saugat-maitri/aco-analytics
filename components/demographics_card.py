import dash_bootstrap_components as dbc
from dash import html


def demographics_card(title, value, comparison_value, comparison_period, value_suffix=None):
    display_value = f"{value}{value_suffix}" if value_suffix else value
    comparison_display_value = f"{comparison_value}{value_suffix}" if value_suffix else comparison_value

    percentage_change = ((value - comparison_value) / comparison_value * 100) if comparison_value != 0 else 0
    percentage_change_str = f"{percentage_change:+.1f}%"

    return dbc.Card(
            dbc.CardBody(
                [
                    html.P(
                        [
                            html.H6(
                                title,
                                className="text-teal-blue",
                                style={"font-size": "18px"},
                            ),
                            html.H1(
                                display_value,
                                style={"font-size": "52px"},
                            ),
                            html.P([
                                html.Span(
                                    f"{comparison_period}: ",
                                    className="text-muted",
                                ),
                                html.Span(
                                    comparison_display_value,
                                    className="fw-semibold",
                                ),
                            ]),
                            html.P([
                                html.Span("Change: ", className="text-muted"),
                                html.Span(percentage_change_str, className="fw-semibold"),
                            ]),
                        ],
                        className="d-flex flex-column gap-1",
                    ),
                ]
            )
        )
