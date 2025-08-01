import dash_bootstrap_components as dbc
from dash import html
import plotly.graph_objs as go

def kpi_card(title, value, comparison_value, expected_value, comparison_id):
    try:
        value_float = float(value)
        comparison_float = float(comparison_value)
        change_ratio = (value_float - comparison_float) / comparison_float if comparison_float != 0 else 0
        comparison_percent = f"{change_ratio:+.1%}"  # + adds sign
        arrow = "▲" if change_ratio >= 0 else "▼"
        arrow_color = "red" if change_ratio >= 0 else "green"
    except (TypeError, ValueError, ZeroDivisionError):
        comparison_percent = "N/A"
        arrow = ""
        arrow_color = "black"

    is_utilization = comparison_id == "comparison-utilization"
    display_value = f"{float(value):,.0f}" if is_utilization else f"${float(value):,.0f}"
    comparison_display = f"{float(comparison_value):,.0f}" if is_utilization else f"${float(comparison_value):,.0f}"

    return dbc.Card([
        dbc.CardBody([
            dbc.Row([
                dbc.Col([
                    html.H6(title, className="fw-semibold"),
                    html.H1(display_value, className="my-2 fw-semibold", style={"font-size": "56px"}),
                    html.P([
                        html.Span(className="text-muted", id=comparison_id),
                        html.Span(": "),
                        html.Span(comparison_display, className="fw-semibold")
                    ], className="text-nowrap"),
                    html.P([
                        html.Span("PMPM Expected: ", className="text-muted"),
                        html.Span(expected_value, className="fw-semibold")
                    ], className="text-nowrap"),
                ], width=7),
                dbc.Col([
                    html.Div([
                        html.P([
                            comparison_percent,
                            html.Span(arrow, className="ms-2")
                        ], className="fw-semibold", style={"color": arrow_color, "fontSize": "18px"}),
                        html.P("vs comparison period", style={"fontSize": "14px"}),
                    ], className="mb-4 lh-sm"),
                    html.Div([
                        html.P([
                            "0.0%",  # Replace with real expected delta if needed
                            html.Span("▲", className="ms-2")
                        ], className="fw-semibold", style={"color": "red", "fontSize": "18px"}),
                        html.P("vs expected", style={"fontSize": "14px"}),
                    ], className="lh-sm")
                ], width=5, className="text-end"),
            ]),
        ])
    ])


def pmpm_vs_expected_bar():
    encounter_groups = ['inpatient', 'outpatient', 'office based', 'other']
    differences = [445, 362, 179, 51]
    colors = ['#ed3030' if val > 400 else '#428c8d' for val in differences]

    fig = go.Figure(go.Bar(
        x=differences,
        y=encounter_groups,
        orientation='h',
        marker_color=colors,
        text=[f"${abs(val)} {'▲' if val > 400 else '▼'}" for val in differences],
        textposition='outside'
    ))

    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=20),
        yaxis=dict(autorange="reversed"),
        plot_bgcolor='white'
    )
    return fig

def line_chart(title):
    import numpy as np
    import pandas as pd

    # Mock data
    dates = pd.date_range(start='2022-01-01', periods=36, freq='ME')
    values = np.random.randint(800, 1200, size=36)

    fig = go.Figure(go.Scatter(
        x=dates,
        y=values,
        mode='lines',
        line=dict(color='#64b0e1')
    ))

    fig.update_layout(
        # title=title,
        margin=dict(l=20, r=20, t=0, b=20),
        plot_bgcolor='white',
        height=100,
        xaxis_title='',
        xaxis=dict(showticklabels=False),
    )

    return fig

def cost_drivers_bar():
    categories = [
        "acute inpatient", "outpatient surgery", "inpatient skilled nursing", "office visit surgery",
        "outpatient hospital or clinic", "home health", "office visit", "emergency department",
        "outpatient hospice", "office visit injections", "outpatient injections", "dialysis"
    ]
    values = [368, 97, 75, 60, 53, 47, 45, 42, 34, 33, 26, 26]

    fig = go.Figure(go.Bar(
        x=values,
        y=categories,
        orientation='h',
        marker_color=['#ed3030' if v > 60 else '#428c8d' for v in values],
        text=[f"${v}" for v in values],
        textposition='outside'
    ))

    fig.update_layout(
        height=300,
        yaxis=dict(autorange="reversed"),
        margin=dict(l=20, r=20, t=20, b=20),
        plot_bgcolor='white'
    )

    return fig


def demographics_card():
    return dbc.Card([
        dbc.CardBody([
            html.H5("Demographics", className="text-teal-blue"),
            html.P([
                html.Span("Monthly Enrollment:"),
                html.Span("7,823")
            ], className="d-flex justify-content-between"),
            html.P([
                html.Span("Average Age:"),
                html.Span("73.55")
            ], className="d-flex justify-content-between"),
            html.P([
                html.Span("% Female:"),
                html.Span("53.5%")
            ], className="d-flex justify-content-between"),
            html.P([
                html.Span("Average Risk:"),
                html.Span("53.5%")
            ], className="d-flex justify-content-between"),
        ])
    ], style={"font-size": "14px"})


def risk_distribution_scatter():
    import numpy as np

    np.random.seed(0)
    x = np.random.rand(500)
    y = np.random.rand(500) * 10

    fig = go.Figure(go.Scatter(
        x=x,
        y=y,
        mode='markers',
        marker=dict(symbol='diamond', color='deepskyblue', size=6, opacity=0.5)
    ))

    fig.update_layout(
        height=170,
        margin=dict(l=20, r=20, t=20, b=20),
        plot_bgcolor='white'
    )

    return fig
