import dash_bootstrap_components as dbc
from dash import html


def metric_card(title, value, format_as_currency=False):
    """Create a simple metric card with title and value.

    Args:
        title (str): The title/label for the metric
        value (str/int/float): The main value to display
        format_as_currency (bool, optional): Whether to format value as currency. Defaults to False.
        color (str, optional): Bootstrap color theme for the card. Defaults to "primary".

    Returns:
        dbc.Card: A Dash Bootstrap Component card with the metric
    """
    try:
        # Format the value
        if format_as_currency:
            display_value = f"${float(value):,.0f}"
        elif isinstance(value, (int, float)):
            display_value = f"{float(value):,.0f}"
        else:
            display_value = str(value)
    except (TypeError, ValueError):
        display_value = "N/A"

    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H6(
                        title,
                        className="card-title text-muted mb-2",
                        style={"font-size": "14px"},
                    ),
                    html.H2(
                        display_value,
                        className="fw-semibold mb-1",
                        style={"font-size": "2.5rem"},
                    ),
                ]
            )
        ],
        className="h-100",
    )


def metric_card_with_icon(
    title,
    value,
    icon_class=None,
    subtitle=None,
    format_as_currency=False,
    color="primary",
):
    """Create a metric card with an icon.

    Args:
        title (str): The title/label for the metric
        value (str/int/float): The main value to display
        icon_class (str, optional): CSS class for the icon (e.g., "fas fa-users")
        subtitle (str, optional): Optional subtitle text below the value
        format_as_currency (bool, optional): Whether to format value as currency. Defaults to False.
        color (str, optional): Bootstrap color theme for the card. Defaults to "primary".

    Returns:
        dbc.Card: A Dash Bootstrap Component card with the metric and icon
    """
    try:
        # Format the value
        if format_as_currency:
            display_value = f"${float(value):,.0f}"
        elif isinstance(value, (int, float)):
            display_value = f"{float(value):,.0f}"
        else:
            display_value = str(value)
    except (TypeError, ValueError):
        display_value = "N/A"

    return dbc.Card(
        [
            dbc.CardBody(
                [
                    dbc.Row(
                        [
                            dbc.Col(
                                [
                                    html.H6(
                                        title,
                                        className="card-title text-muted mb-2",
                                        style={"font-size": "14px"},
                                    ),
                                    html.H2(
                                        display_value,
                                        className="fw-bold mb-1",
                                        style={
                                            "font-size": "2.5rem",
                                            "color": f"var(--bs-{color})",
                                        },
                                    ),
                                    html.P(
                                        subtitle,
                                        className="text-muted mb-0",
                                        style={"font-size": "12px"},
                                    )
                                    if subtitle
                                    else None,
                                ],
                                width=8,
                            ),
                            dbc.Col(
                                [
                                    html.I(
                                        className=f"{icon_class} fa-2x",
                                        style={"color": f"var(--bs-{color})"},
                                    ),
                                ],
                                width=4,
                                className="d-flex align-items-center justify-content-end",
                            )
                            if icon_class
                            else None,
                        ]
                    ),
                ]
            )
        ],
        className="h-100",
    )
