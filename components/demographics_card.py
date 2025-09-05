import dash_bootstrap_components as dbc
from dash import html


def demographics_card(data):
    # Extract scalar values from the data (handle both Series and DataFrame)
    try:
        demographic_data = data.iloc[0].to_dict()
        total_member_months = int(demographic_data.get("TOTAL_MEMBER_MONTHS", 0))
        avg_age = demographic_data.get("AVG_AGE") or 0
        percent_female = demographic_data.get("PERCENT_FEMALE") or 0
        avg_risk_score = demographic_data.get("AVG_RISK_SCORE") or 0
    except Exception as e:
        print(f"Error extracting demographics data: {e}")
        total_member_months = 0
        avg_age = 0.0
        percent_female = 0.0
        avg_risk_score = 0.0

    return dbc.Card(
        [
            dbc.CardBody(
                [
                    html.H5("Demographics", className="text-teal-blue mb-3"),
                    html.P(
                        [
                            html.Span("Monthly Enrollment:"),
                            html.Span(f"{total_member_months:,}"),
                        ],
                        className="d-flex justify-content-between mb-2",
                    ),
                    html.P(
                        [html.Span("Average Age:"), html.Span(f"{avg_age:.1f}")],
                        className="d-flex justify-content-between mb-2",
                    ),
                    html.P(
                        [html.Span("% Female:"), html.Span(f"{percent_female:.1f}%")],
                        className="d-flex justify-content-between mb-2",
                    ),
                    html.P(
                        [
                            html.Span("Average Risk:"),
                            html.Span(f"{avg_risk_score:.1f}"),
                        ],
                        className="d-flex justify-content-between mb-0",
                    ),
                ],
                className="h-100",
            )
        ],
        style={"font-size": "14px"},
    )
