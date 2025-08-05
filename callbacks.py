from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from dash import Input, Output, callback
import pandas as pd
import plotly.graph_objs as go
from functools import lru_cache
from typing import Tuple

from components import condition_ccsr_graph, kpi_card
from data.db_manager import fetch_data


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

def get_comparison_period(start_date_str, end_date_str, comparison_period):
    start = datetime.strptime(start_date_str, "%Y-%m-%d")
    end = datetime.strptime(end_date_str, "%Y-%m-%d")
    period_months = (end.year - start.year) * 12 + (end.month - start.month) + 1

    def dt_to_yyyymm(dt):
        return dt.year * 100 + dt.month

    if comparison_period == "Same Period Last Year":
        comp_start = start.replace(year=start.year - 1)
        comp_end = end.replace(year=end.year - 1)

    elif comparison_period == "Previous Year":
        comp_start = datetime(start.year - 1, 1, 1)
        comp_end = datetime(start.year - 1, 12, 31)

    elif comparison_period == "Previous Period":
        comp_end = start - timedelta(days=1)
        comp_start = comp_end - relativedelta(months=period_months - 1)
        comp_start = comp_start.replace(day=1)  # align to start of month

    elif comparison_period == "Previous Month":
        comp_start = (start.replace(day=1) - timedelta(days=1)).replace(day=1)
        comp_end = comp_start + relativedelta(months=1) - timedelta(days=1)

    elif comparison_period == "Previous Quarter":
        q = (start.month - 1) // 3 + 1
        if q == 1:
            comp_start = datetime(start.year - 1, 10, 1)
        else:
            comp_start = datetime(start.year, 3 * (q - 2) + 1, 1)
        comp_end = comp_start + relativedelta(months=3) - timedelta(days=1)

    elif comparison_period == "Previous 18 Months":
        comp_end = start - timedelta(days=1)
        comp_start = comp_end - relativedelta(months=18)
        comp_start = comp_start.replace(day=1)

    else:
        comp_start, comp_end = start, end

    return dt_to_yyyymm(start), dt_to_yyyymm(end), dt_to_yyyymm(comp_start.date()), dt_to_yyyymm(comp_end.date())

@callback(
    Output("comparison-pmpm", "children"),
    Output("comparison-utilization", "children"),
    Output("comparison-cost", "children"),
    Input("comparison-period-dropdown", "value")
)
def update_comparison_text(comparison_period):
    return comparison_period, comparison_period, comparison_period

@callback(
    Output("pmpm-cost-card", "children"),
    Output("utilization-card", "children"),
    Output("cost-per-encounter-card", "children"),
    Output("condition-ccsr", "children"),
    Input("my-date-picker-range", "start_date"),
    Input("my-date-picker-range", "end_date"),
    Input("comparison-period-dropdown", "value")
)
def update_kpi_cards(start_date, end_date, comparison_period):
    claims_agg, member_months = load_data()

    def calc_kpis(start_date, end_date):

        claims_agg_df = claims_agg[(claims_agg["YEAR_MONTH"] >= start_date) & (claims_agg["YEAR_MONTH"] <= end_date)]
        member_months_df = member_months[(member_months["YEAR_MONTH"] >= start_date) & (member_months["YEAR_MONTH"] <= end_date)]

        mm = member_months_df[["PERSON_ID", "YEAR_MONTH"]].drop_duplicates().shape[0]
        encounters = claims_agg_df["ENCOUNTER_ID"].nunique()
        paid = claims_agg_df["PAID_AMOUNT"].sum()
        pmpm = paid / mm if mm else 0
        utilization = (encounters / mm * 12000) if mm else 0
        cpe = paid / encounters if encounters else 0
        return pmpm, utilization, cpe

    start, end, comp_start, comp_end = get_comparison_period(start_date, end_date, comparison_period)

    pmpm_main, util_main, cpe_main = calc_kpis(start, end)
    pmpm_comp, util_comp, cpe_comp = calc_kpis(comp_start, comp_end)

    def calculate_ccsr_pmpm(start_date, end_date):
        claims_agg_df = claims_agg[(claims_agg["YEAR_MONTH"] >= start_date) & (claims_agg["YEAR_MONTH"] <= end_date)]
        member_months_df = member_months[(member_months["YEAR_MONTH"] >= start_date) & (member_months["YEAR_MONTH"] <= end_date)]

        if claims_agg_df.empty or member_months_df.empty:
            return 0

        ccsr_pmpm = (
            claims_agg_df.groupby("CCSR_CATEGORY_DESCRIPTION")["PAID_AMOUNT"]
            .sum()
            .reset_index()
            .rename(columns={"PAID_AMOUNT": "TOTAL_PAID"})
            .sort_values('TOTAL_PAID', ascending=False)
        )
        total_member_months = member_months_df["PERSON_ID"].nunique()
        if total_member_months == 0:
            ccsr_pmpm["PMPM"] = 0
        else:
            ccsr_pmpm["PMPM"] = ccsr_pmpm["TOTAL_PAID"] / total_member_months
        return ccsr_pmpm

    ccsr_pmpm = calculate_ccsr_pmpm(start, end)

    # Comparison values (dummy for now)
    expected = 300
    # Return dynamic cards
    return (
        kpi_card("PMPM Cost", pmpm_main, pmpm_comp, expected, "comparison-pmpm"),
        kpi_card("Utilization (PKPY)", util_main, util_comp, expected, "comparison-utilization"),
        kpi_card("Cost Per Encounter", cpe_main, cpe_comp, expected, "comparison-cost"),
        condition_ccsr_graph(ccsr_pmpm)
    )

@callback(
    Output("pmpm-trend", "figure"),
    Input("my-date-picker-range", "start_date"),
    Input("my-date-picker-range", "end_date"),
    Input("comparison-period-dropdown", "value")
)
def update_pmpm_trend(start_date, end_date, comparison_period):
    import pandas as pd
    from pandas.tseries.offsets import DateOffset

    # Load and prepare data
    claims_agg, member_months = load_data()

    amount_by_month = claims_agg.groupby("YEAR_MONTH").agg(PAID_AMOUNT=('PAID_AMOUNT', 'sum')).reset_index()
    mm_grouped = member_months.groupby("YEAR_MONTH")["PERSON_ID"].nunique().reset_index()

    amount_by_month["DATE"] = pd.to_datetime(amount_by_month["YEAR_MONTH"], format="%Y%m")
    mm_grouped["DATE"] = pd.to_datetime(mm_grouped["YEAR_MONTH"], format="%Y%m")

    df = pd.merge(amount_by_month, mm_grouped, on="DATE", how="inner")
    df["PMPM"] = df["PAID_AMOUNT"] / df["PERSON_ID"]
    df = df.sort_values("DATE").reset_index(drop=True)

    # Selected period
    start = pd.to_datetime(start_date).replace(day=1)
    end = pd.to_datetime(end_date).replace(day=1)
    selected_months = pd.date_range(start=start, end=end, freq='MS')

    # Current period data
    current_df = df[df["DATE"].isin(selected_months)]
    current_data = list(zip(current_df["DATE"], current_df["PMPM"]))

    # Determine comparison data
    comparison_data = []

    for month in selected_months:
        # Determine comparison window
        if comparison_period == "Previous Month":
            comp_start = comp_end = month - DateOffset(months=1)
        elif comparison_period == "Previous Year":
            comp_start = comp_end = month - DateOffset(years=1)
        elif comparison_period == "Same Period Last Year":
            comp_start = comp_end = month - DateOffset(years=1)
        elif comparison_period == "Previous Quarter":
            current_quarter_first_month = ((month.month - 1) // 3) * 3 + 1
            current_quarter_start_date = pd.Timestamp(month.year, current_quarter_first_month, 1)
            comp_start = current_quarter_start_date - DateOffset(months=3)
            comp_end = current_quarter_start_date - DateOffset(months=1)
        elif comparison_period == "Previous 18 Months":
            comp_start = month - DateOffset(months=18)
            comp_end = month - DateOffset(months=1)
        else:
            continue  # unknown comparison period

        # Get comparison date range
        comp_range = pd.date_range(start=comp_start, end=comp_end, freq='MS')
        comp_df = df[df["DATE"].isin(comp_range)]

        # Calculate PMPM from range
        if not comp_df.empty:
            total_paid = comp_df["PAID_AMOUNT"].sum()
            total_members = comp_df["PERSON_ID"].sum()
            if total_members > 0:
                avg_pmpm = total_paid / total_members
                comparison_data.append((month, avg_pmpm))

    # Plot
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
    Output("pkpy-trend", "figure"),
    Input("my-date-picker-range", "start_date"),
    Input("my-date-picker-range", "end_date"),
    Input("comparison-period-dropdown", "value")
)
def update_pkpy_trend(start_date, end_date, comparison_period):
    import pandas as pd
    from pandas.tseries.offsets import DateOffset

    # Load and prepare data
    claims_agg, member_months = load_data()
    encounters_by_month = claims_agg.groupby("YEAR_MONTH")["ENCOUNTER_ID"].nunique().reset_index()
    mm_grouped = member_months.groupby("YEAR_MONTH")["PERSON_ID"].nunique().reset_index()

    encounters_by_month["DATE"] = pd.to_datetime(encounters_by_month["YEAR_MONTH"], format="%Y%m")
    mm_grouped["DATE"] = pd.to_datetime(mm_grouped["YEAR_MONTH"], format="%Y%m")

    df = pd.merge(encounters_by_month, mm_grouped, on="DATE", how="inner")
    df["PKPY"] = (df["ENCOUNTER_ID"] / df["PERSON_ID"]) * 12000
    df = df.sort_values("DATE").reset_index(drop=True)

    # Selected period
    start = pd.to_datetime(start_date).replace(day=1)
    end = pd.to_datetime(end_date).replace(day=1)
    selected_months = pd.date_range(start=start, end=end, freq='MS')

    # Current period data
    current_df = df[df["DATE"].isin(selected_months)]
    current_data = list(zip(current_df["DATE"], current_df["PKPY"]))

    # Determine comparison data
    comparison_data = []

    for month in selected_months:
        # Determine comparison window
        if comparison_period == "Previous Month":
            comp_start = comp_end = month - DateOffset(months=1)
        elif comparison_period == "Previous Year":
            comp_start = comp_end = month - DateOffset(years=1)
        elif comparison_period == "Same Period Last Year":
            comp_start = comp_end = month - DateOffset(years=1)
        elif comparison_period == "Previous Quarter":
            current_quarter_first_month = ((month.month - 1) // 3) * 3 + 1
            current_quarter_start_date = pd.Timestamp(month.year, current_quarter_first_month, 1)
            comp_start = current_quarter_start_date - DateOffset(months=3)
            comp_end = current_quarter_start_date - DateOffset(months=1)
        elif comparison_period == "Previous 18 Months":
            comp_start = month - DateOffset(months=18)
            comp_end = month - DateOffset(months=1)
        else:
            continue  # unknown comparison period

        # Get comparison date range
        comp_range = pd.date_range(start=comp_start, end=comp_end, freq='MS')
        comp_df = df[df["DATE"].isin(comp_range)]

        # Calculate PMPM from range
        if not comp_df.empty:
            total_encounters = comp_df["ENCOUNTER_ID"].sum()
            total_members = comp_df["PERSON_ID"].sum()
            if total_members > 0:
                avg_pkpy = (total_encounters / total_members) * 12000
                comparison_data.append((month, avg_pkpy))

    # Plot
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
        showlegend=False
    )

    return fig


@callback(
    Output("cost-per-trend", "figure"),
    Input("my-date-picker-range", "start_date"),
    Input("my-date-picker-range", "end_date"),
    Input("comparison-period-dropdown", "value")
)
def update_cost_per_trend(start_date, end_date, comparison_period):
    import pandas as pd
    from pandas.tseries.offsets import DateOffset

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
        # Determine comparison window
        if comparison_period == "Previous Month":
            comp_start = comp_end = month - DateOffset(months=1)
        elif comparison_period == "Previous Year":
            comp_start = comp_end = month - DateOffset(years=1)
        elif comparison_period == "Same Period Last Year":
            comp_start = comp_end = month - DateOffset(years=1)
        elif comparison_period == "Previous Quarter":
            current_quarter_first_month = ((month.month - 1) // 3) * 3 + 1
            current_quarter_start_date = pd.Timestamp(month.year, current_quarter_first_month, 1)
            comp_start = current_quarter_start_date - DateOffset(months=3)
            comp_end = current_quarter_start_date - DateOffset(months=1)
        elif comparison_period == "Previous 18 Months":
            comp_start = month - DateOffset(months=18)
            comp_end = month - DateOffset(months=1)
        else:
            continue  # unknown comparison period

        # Get comparison date range
        comp_range = pd.date_range(start=comp_start, end=comp_end, freq='MS')
        comp_df = monthly_agg[monthly_agg["YEAR_MONTH"].isin(comp_range)]

        # Calculate PMPM from range
        if not comp_df.empty:
            total_paid = comp_df["PAID_AMOUNT"].sum()
            total_encounters = comp_df["ENCOUNTERS"].sum()
            if total_encounters > 0:
                avg_cost_per_encounter = total_paid / total_encounters
                comparison_data.append((month, avg_cost_per_encounter))

    # Plot
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
        showlegend=False
    )

    return fig