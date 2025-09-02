import calendar
from datetime import date

import dash_bootstrap_components as dbc
import plotly.express as px
import plotly.graph_objs as go
from dash import dcc, html

from data.db_query import query_sqlite


def no_data_figure(message="No data available for the selected period"):
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=18, color="gray"),
        align="center"
    )
    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=0, r=0, t=40, b=0),
    )
    return fig

def header():
    query = "SELECT DISTINCT(YEAR_MONTH) FROM FACT_CLAIMS"
    claims_agg = query_sqlite(query)

    # Use integer division to extract year from YEAR_MONTH which is in YYYYMM format
    years = sorted((claims_agg["YEAR_MONTH"] // 100).unique())
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


def pmpm_vs_expected_bar(data):
    if data is None or data.empty:
        return no_data_figure()
    
    # This is just for demo purposes, will be updated
    colors = ['#ed3030' if val > 400 else '#428c8d' for val in data["PMPM"]]

    fig = go.Figure(go.Bar(
        x=data["PMPM"],
        y=data["ENCOUNTER_GROUP"],
        orientation='h',
        marker_color=colors,
        text=[f"${v:,.0f}" for v in data['PMPM']],
        textposition='outside',
        hovertemplate=('Encounter Group: %{customdata}<br>PMPM: %{text}<extra></extra>'),
        customdata=data['ENCOUNTER_GROUP'],
        texttemplate="$%{x:,.0f}"
    ))

    fig.update_layout(
        margin=dict(l=20, r=20, t=20, b=0),
        yaxis=dict(autorange="reversed"),
        xaxis=dict(showticklabels=False),
        plot_bgcolor='white',
        clickmode='event+select'
    )
    return fig

def encounter_type_pmpm_bar(data):
    if data is None or data.empty:
        return no_data_figure()
    
    # This is just for demo purposes, will be updated
    colors = ['#ed3030' if val > 400 else '#428c8d' for val in data["PMPM"]]

    fig = go.Figure(go.Bar(
        x=data["PMPM"],
        y=data["ENCOUNTER_TYPE"],
        orientation='h',
        marker_color=colors,
        text=[f"${v:,.0f}" for v in data['PMPM']],
        textposition='outside',
        hovertemplate=('Encounter Type: %{customdata}<br>PMPM: %{text}<extra></extra>'),
        customdata=data['ENCOUNTER_TYPE'],
    ))

    fig.update_layout(
        height=max(300, 20 * len(data)),
        margin=dict(l=20, r=20, t=20, b=0),
        yaxis=dict(autorange="reversed"),
        xaxis=dict(showticklabels=False),
        plot_bgcolor='white',
        autosize=True,
        clickmode='event+select'
    )

    return fig


def condition_ccsr_cost_driver_graph(data):
    # Handle None or empty data
    if data is None or data.empty:
        return no_data_figure()

    # Truncate long category descriptions
    def truncate_text(text, max_length=30):
        return text[:max_length] + '...' if len(text) > max_length else text
    
    data['TRUNCATED_CATEGORY'] = data['CCSR_CATEGORY_DESCRIPTION'].apply(
        lambda x: truncate_text(x, 30)
    )

    fig = go.Figure(go.Bar(
        x=data['PMPM'],
        y=data['TRUNCATED_CATEGORY'],
        orientation='h',
        marker_color='#64AFE0',
        text=[f"${v:,.0f}" for v in data['PMPM']],
        textposition='outside',
        hovertemplate=('CCSR Category:  %{customdata}<br>PMPM:  %{text}<extra></extra>'),
        customdata=data['CCSR_CATEGORY_DESCRIPTION'],
    ))
    
    # Calculate x-axis range with padding for text labels
    max_value = data['PMPM'].max() if not data.empty else 0
    x_range_max = max_value * 1.3  # Add 30% padding for text labels
    
    fig.update_layout(
        height=max(300, 20 * len(data)),
        yaxis=dict(
            autorange="reversed",
            tickfont=dict(size=10)
        ),
        xaxis=dict(
            title="PMPM",
            tickformat="$,",
            range=[0, x_range_max]  # Set explicit range with padding
        ),
        hoverlabel=dict(
            bgcolor='white'
        ),
        margin=dict(l=20, r=20, t=20, b=20),
        plot_bgcolor='white',
        autosize=True,
        clickmode='event+select'
    )

    return fig

def trend_chart(current_data, comparison_data):
    fig = go.Figure()

    if current_data:
        x_cur, y_cur = zip(*current_data)
        fig.add_trace(go.Scatter(
            x=x_cur,
            y=y_cur,
            mode='lines+markers',
            name='Current',
            line=dict(color='#64b0e1')
        ))

    if comparison_data:
        x_cmp, y_cmp = zip(*comparison_data)
        fig.add_trace(go.Scatter(
            x=x_cmp,
            y=y_cmp,
            mode='lines+markers',
            name='Comparison',
            line=dict(color='gray', dash='dash')
        ))

    fig.update_layout(
        margin=dict(l=20, r=20, t=30, b=30),
        plot_bgcolor='white',
        height=100,
        hovermode='x unified',
        showlegend=False,
    )

    return fig

def demographics_card(data):   
    # Extract scalar values from the data (handle both Series and DataFrame)
    try:
        demographic_data = data.iloc[0].to_dict()
        total_member_months = int(demographic_data.get('TOTAL_MEMBER_MONTHS', 0))
        avg_age = demographic_data.get('AVG_AGE') or 0
        percent_female = demographic_data.get('PERCENT_FEMALE') or 0
        avg_risk_score = demographic_data.get('AVG_RISK_SCORE') or 0
    except Exception as e:
        print(f"Error extracting demographics data: {e}")
        total_member_months = 0
        avg_age = 0.0
        percent_female = 0.0
        avg_risk_score = 0.0
    
    return dbc.Card([
        dbc.CardBody([
            html.H5("Demographics", className="text-teal-blue mb-3"),
            html.P([
                html.Span("Monthly Enrollment:"),
                html.Span(f"{total_member_months:,}")
            ], className="d-flex justify-content-between mb-2"),
            html.P([
                html.Span("Average Age:"),
                html.Span(f"{avg_age:.1f}")
            ], className="d-flex justify-content-between mb-2"),
            html.P([
                html.Span("% Female:"),
                html.Span(f"{percent_female:.1f}%")
            ], className="d-flex justify-content-between mb-2"),
            html.P([
                html.Span("Average Risk:"),
                html.Span(f"{avg_risk_score:.1f}")
            ], className="d-flex justify-content-between mb-0"),
        ], className="h-100")
    ], style={"font-size": "14px"})


def risk_distribution_card(data):
    box_height = 117
    if data is None or data.empty:
        return no_data_figure()

    fig = px.box(data, y='NORMALIZED_RISK_SCORE', points="outliers")

    fig.update_layout(
        plot_bgcolor='white',
        showlegend=False,
        yaxis_title="",
        xaxis_title="",
        margin=dict(l=10, r=10, t=10, b=10),
        height=box_height,
    )
    # Clean up grid and axis lines for a cleaner look
    fig.update_xaxes(showgrid=False, visible=False)
    fig.update_yaxes(showgrid=True, zeroline=False, ticks="outside", showline=True, linewidth=1, linecolor="#ccc")
    return fig
