from dash import Input, Output, callback
import pandas as pd
import plotly.graph_objs as go
from functools import lru_cache
from typing import Tuple
from pandas import DateOffset

from data import fetch_data


@lru_cache(maxsize=2)
def load_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load and cache claims and member data from Snowflake."""
    claims_query = "SELECT * FROM FACT_CLAIMS limit 1000"
    member_query = "SELECT * FROM FACT_MEMBER_MONTHS limit 1000"

    claims_agg = fetch_data(claims_query)
    member_months = fetch_data(member_query)
    claims_agg["YEAR_MONTH"] = claims_agg["YEAR_MONTH"].astype(int)
    member_months["YEAR_MONTH"] = member_months["YEAR_MONTH"].astype(int)

    return claims_agg, member_months

def get_comparison_offset(month, comparison_period):
    if comparison_period == "Previous Month":
        comp_start = comp_end = month - DateOffset(months=1)
    elif comparison_period in ("Previous Year", "Same Period Last Year"):
        comp_start = comp_end = month - DateOffset(years=1)
    elif comparison_period == "Previous Quarter":
        first_month = ((month.month - 1) // 3) * 3 + 1
        start_of_quarter = pd.Timestamp(month.year, first_month, 1)
        comp_start = start_of_quarter - DateOffset(months=3)
        comp_end = start_of_quarter - DateOffset(months=1)
    elif comparison_period == "Previous 18 Months":
        comp_start = month - DateOffset(months=18)
        comp_end = month - DateOffset(months=1)
    else:
        return pd.DatetimeIndex([])
    return pd.date_range(start=comp_start, end=comp_end, freq='MS')

def plot_trend(current_data, comparison_data):
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

@callback(
    Output("pmpm-trend", "figure"),
    Input("my-date-picker-range", "start_date"),
    Input("my-date-picker-range", "end_date"),
    Input("comparison-period-dropdown", "value")
)
def update_pmpm_trend(start_date, end_date, comparison_period):
    # Load and prepare data
    claims_agg, member_months = load_data()

    amount_by_month = claims_agg.groupby("YEAR_MONTH").agg(PAID_AMOUNT=('PAID_AMOUNT', 'sum')).reset_index()
    mm_grouped = member_months.groupby("YEAR_MONTH")["PERSON_ID"].nunique().reset_index()

    df = pd.merge(amount_by_month, mm_grouped, on="YEAR_MONTH", how="inner")
    df["PMPM"] = df["PAID_AMOUNT"] / df["PERSON_ID"]
    df = df.sort_values("YEAR_MONTH").reset_index(drop=True)
    df["YEAR_MONTH"] = pd.to_datetime(mm_grouped["YEAR_MONTH"], format="%Y%m")

    # Selected period
    start = pd.to_datetime(start_date).replace(day=1)
    end = pd.to_datetime(end_date).replace(day=1)
    selected_months = pd.date_range(start=start, end=end, freq='MS')

    # Current period data
    current_df = df[df["YEAR_MONTH"].isin(selected_months)]
    current_data = list(zip(current_df["YEAR_MONTH"], current_df["PMPM"]))

    # Determine comparison data
    comparison_data = []
    for month in selected_months:
        comp_range = get_comparison_offset(month, comparison_period)
        comp_df = df[df["YEAR_MONTH"].isin(comp_range)]

        # Calculate PMPM from range
        if not comp_df.empty:
            total_paid = comp_df["PAID_AMOUNT"].sum()
            total_members = comp_df["PERSON_ID"].sum()
            if total_members > 0:
                avg_pmpm = total_paid / total_members
                comparison_data.append((month, avg_pmpm))

    # Plot
    return plot_trend(current_data, comparison_data)


@callback(
    Output("pkpy-trend", "figure"),
    Input("my-date-picker-range", "start_date"),
    Input("my-date-picker-range", "end_date"),
    Input("comparison-period-dropdown", "value")
)
def update_pkpy_trend(start_date, end_date, comparison_period):
    # Load and prepare data
    claims_agg, member_months = load_data()
    
    encounters_by_month = claims_agg.groupby("YEAR_MONTH")["ENCOUNTER_ID"].nunique().reset_index()
    mm_grouped = member_months.groupby("YEAR_MONTH")["PERSON_ID"].nunique().reset_index()

    df = pd.merge(encounters_by_month, mm_grouped, on="YEAR_MONTH", how="inner")
    df["PKPY"] = (df["ENCOUNTER_ID"] / df["PERSON_ID"]) * 12000
    df = df.sort_values("YEAR_MONTH").reset_index(drop=True)
    df["YEAR_MONTH"] = pd.to_datetime(mm_grouped["YEAR_MONTH"], format="%Y%m")

    # Selected period
    start = pd.to_datetime(start_date).replace(day=1)
    end = pd.to_datetime(end_date).replace(day=1)
    selected_months = pd.date_range(start=start, end=end, freq='MS')

    # Current period data
    current_df = df[df["YEAR_MONTH"].isin(selected_months)]
    current_data = list(zip(current_df["YEAR_MONTH"], current_df["PKPY"]))

    # Determine comparison data
    comparison_data = []
    for month in selected_months:
        comp_range = get_comparison_offset(month, comparison_period)
        comp_df = df[df["YEAR_MONTH"].isin(comp_range)]

        # Calculate PMPM from range
        if not comp_df.empty:
            total_encounters = comp_df["ENCOUNTER_ID"].sum()
            total_members = comp_df["PERSON_ID"].sum()
            if total_members > 0:
                avg_pkpy = (total_encounters / total_members) * 12000
                comparison_data.append((month, avg_pkpy))

    # Plot
    return plot_trend(current_data, comparison_data)


@callback(
    Output("cost-per-trend", "figure"),
    Input("my-date-picker-range", "start_date"),
    Input("my-date-picker-range", "end_date"),
    Input("comparison-period-dropdown", "value")
)
def update_cost_per_trend(start_date, end_date, comparison_period):
    # Load and prepare data
    claims_agg, member_months = load_data()

    monthly_agg = claims_agg.groupby("YEAR_MONTH").agg(
        PAID_AMOUNT=('PAID_AMOUNT', 'sum'),
        ENCOUNTERS=('ENCOUNTER_ID', 'nunique')
    ).reset_index().assign(
        COST_PER_ENCOUNTER=lambda df: df['PAID_AMOUNT'] / df['ENCOUNTERS']
    )
    monthly_agg["YEAR_MONTH"] = pd.to_datetime(monthly_agg["YEAR_MONTH"], format="%Y%m")

    # Selected period
    start = pd.to_datetime(start_date).replace(day=1)
    end = pd.to_datetime(end_date).replace(day=1)
    selected_months = pd.date_range(start=start, end=end, freq='MS')

    # Current period data
    current_df = monthly_agg[monthly_agg["YEAR_MONTH"].isin(selected_months)]
    current_data = list(zip(current_df["YEAR_MONTH"], current_df["COST_PER_ENCOUNTER"]))

    # Determine comparison data
    comparison_data = []

    for month in selected_months:
        # Get comparison date range
        comp_range = get_comparison_offset(month, comparison_period)
        comp_df = monthly_agg[monthly_agg["YEAR_MONTH"].isin(comp_range)]

        # Calculate PMPM from range
        if not comp_df.empty:
            total_paid = comp_df["PAID_AMOUNT"].sum()
            total_encounters = comp_df["ENCOUNTERS"].sum()
            if total_encounters > 0:
                avg_cost_per_encounter = total_paid / total_encounters
                comparison_data.append((month, avg_cost_per_encounter))

    # Plot
    return plot_trend(current_data, comparison_data)