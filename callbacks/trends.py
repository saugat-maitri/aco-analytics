from dash import Input, Output, callback
import pandas as pd
from pandas import DateOffset

from components import trend_chart
from data.db_query import query_sqlite

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

def get_trends_data() -> pd.DataFrame:
    try:
        query = """
            SELECT
                clm.YEAR_MONTH,
                SUM(clm.PAID_AMOUNT) AS TOTAL_PAID,
                COUNT(DISTINCT clm.ENCOUNTER_ID) AS ENCOUNTERS,
                COUNT(DISTINCT mm.PERSON_ID) AS MEMBERS,
                CASE WHEN COUNT(DISTINCT mm.PERSON_ID) > 0
                    THEN SUM(clm.PAID_AMOUNT) * 1.0 / COUNT(DISTINCT mm.PERSON_ID)
                    ELSE 0 END AS PMPM,
                CASE WHEN COUNT(DISTINCT mm.PERSON_ID) > 0
                    THEN (COUNT(DISTINCT clm.ENCOUNTER_ID) * 12000.0 / COUNT(DISTINCT mm.PERSON_ID))
                    ELSE 0 END AS PKPY,
                CASE WHEN COUNT(DISTINCT clm.ENCOUNTER_ID) > 0
                    THEN SUM(clm.PAID_AMOUNT) * 1.0 / COUNT(DISTINCT clm.ENCOUNTER_ID)
                    ELSE 0 END AS COST_PER_ENCOUNTER
            FROM FACT_CLAIMS clm
            JOIN FACT_MEMBER_MONTHS mm
                ON clm.YEAR_MONTH = mm.YEAR_MONTH
            GROUP BY clm.YEAR_MONTH
            ORDER BY clm.YEAR_MONTH
            """
        result = query_sqlite(query)
        if result is not None and not result.empty:
            result["YEAR_MONTH"] = pd.to_datetime(result["YEAR_MONTH"].astype(str), format="%Y%m")
        # Ensure we always return a DataFrame, even if empty
        if result is None:
            return pd.DataFrame(columns=['YEAR_MONTH', 'TOTAL_PAID', 'ENCOUNTERS', 'MEMBERS', 'PMPM', 'PKPY', 'COST_PER_ENCOUNTER'])
        
        return result
        
    except Exception as e:
        print(f"Error in get_trends_data: {e}")
        return pd.DataFrame(columns=['YEAR_MONTH', 'TOTAL_PAID', 'ENCOUNTERS', 'MEMBERS', 'PMPM', 'PKPY', 'COST_PER_ENCOUNTER'])



@callback(
    Output("pmpm-trend", "figure"),
    Input("date-picker-input", "start_date"),
    Input("date-picker-input", "end_date"),
    Input("comparison-period-dropdown", "value")
)
def update_pmpm_trend(start_date, end_date, comparison_period):
    df = get_trends_data()

    start = pd.to_datetime(start_date).replace(day=1)
    end = pd.to_datetime(end_date).replace(day=1)
    selected_months = pd.date_range(start=start, end=end, freq='MS')

    current_data = []
    if not df.empty:
        current_df = df[df["YEAR_MONTH"].isin(selected_months)]
        current_data = list(zip(current_df["YEAR_MONTH"], current_df["PMPM"]))

    comparison_data = []
    for month in selected_months:
        comp_range = get_comparison_offset(month, comparison_period)
        comp_df = df[df["YEAR_MONTH"].isin(comp_range)]
        total_paid = comp_df["TOTAL_PAID"].sum()
        total_members = comp_df["MEMBERS"].sum()
        avg_pmpm = total_paid / total_members if total_members > 0 else 0
        comparison_data.append((month, avg_pmpm))

    return trend_chart(current_data, comparison_data)

@callback(
    Output("pkpy-trend", "figure"),
    Input("date-picker-input", "start_date"),
    Input("date-picker-input", "end_date"),
    Input("comparison-period-dropdown", "value")
)
def update_pkpy_trend(start_date, end_date, comparison_period):
    # Load and prepare data
    df = get_trends_data()

    start = pd.to_datetime(start_date).replace(day=1)
    end = pd.to_datetime(end_date).replace(day=1)
    selected_months = pd.date_range(start=start, end=end, freq='MS')

    current_data = []
    if not df.empty:
        current_df = df[df["YEAR_MONTH"].isin(selected_months)]
        current_data = list(zip(current_df["YEAR_MONTH"], current_df["PKPY"]))

    comparison_data = []
    for month in selected_months:
        comp_range = get_comparison_offset(month, comparison_period)
        comp_df = df[df["YEAR_MONTH"].isin(comp_range)]
        total_encounters = comp_df["ENCOUNTERS"].sum()
        total_members = comp_df["MEMBERS"].sum()
        if total_members > 0:
            avg_pkpy = (total_encounters / total_members) * 12000
            comparison_data.append((month, avg_pkpy))

    return trend_chart(current_data, comparison_data)

@callback(
    Output("cost-per-trend", "figure"),
    Input("date-picker-input", "start_date"),
    Input("date-picker-input", "end_date"),
    Input("comparison-period-dropdown", "value")
)
def update_cost_per_trend(start_date, end_date, comparison_period):
    df = get_trends_data()

    start = pd.to_datetime(start_date).replace(day=1)
    end = pd.to_datetime(end_date).replace(day=1)
    selected_months = pd.date_range(start=start, end=end, freq='MS')

    current_data = []
    if not df.empty:
        current_df = df[df["YEAR_MONTH"].isin(selected_months)]
        current_data = list(zip(current_df["YEAR_MONTH"], current_df["COST_PER_ENCOUNTER"]))

    comparison_data = []
    for month in selected_months:
        comp_range = get_comparison_offset(month, comparison_period)
        comp_df = df[df["YEAR_MONTH"].isin(comp_range)]

        if not comp_df.empty:
            total_paid = comp_df["TOTAL_PAID"].sum()
            total_encounters = comp_df["ENCOUNTERS"].sum()
            if total_encounters > 0:
                avg_cost_per_encounter = total_paid / total_encounters
                comparison_data.append((month, avg_cost_per_encounter))

    return trend_chart(current_data, comparison_data)