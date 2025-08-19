from dash import Input, Output, callback
import pandas as pd
from pandas import DateOffset

from components import trend_chart
from data.db_query import query_sqlite

def get_comparison_offset(month, comparison_period, selected_months=None):
    if comparison_period == "Previous Month":
        comp_start = comp_end = month - DateOffset(months=1)
    elif comparison_period == "Previous Year":
        prev_year = month.year - 1
        comp_start = pd.Timestamp(prev_year, 1, 1)
        comp_end = pd.Timestamp(prev_year, 12, 1)
    elif comparison_period == "Same Period Last Year":
        comp_start = comp_end = month - DateOffset(years=1)
    elif comparison_period == "Previous Period" and selected_months is not None:
        period_length = len(selected_months)
        comp_start = comp_end = month - DateOffset(months=period_length)
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

def get_trends_data(filters) -> pd.DataFrame:
    filter_sql = ""
    if filters:
        filter_clauses = []
        for col, value in filters.items():
            if value is not None:
                filter_clauses.append(f"{col} = '{value}'")
        if filter_clauses:
            filter_sql = " WHERE " + " AND ".join(filter_clauses)
    try:
        query = f"""
            SELECT
                clm.YEAR_MONTH,
                SUM(clm.PAID_AMOUNT) AS TOTAL_PAID,
                COUNT(DISTINCT clm.ENCOUNTER_ID) AS ENCOUNTERS_COUNT,
                COUNT(DISTINCT mm.PERSON_ID) AS MEMBERS_COUNT,
                CASE WHEN COUNT(DISTINCT mm.PERSON_ID) > 0
                    THEN SUM(clm.PAID_AMOUNT) / COUNT(DISTINCT mm.PERSON_ID)
                    ELSE 0 END AS PMPM,
                CASE WHEN COUNT(DISTINCT mm.PERSON_ID) > 0
                    THEN (COUNT(DISTINCT clm.ENCOUNTER_ID) * 12000.0 / COUNT(DISTINCT mm.PERSON_ID))
                    ELSE 0 END AS PKPY,
                CASE WHEN COUNT(DISTINCT clm.ENCOUNTER_ID) > 0
                    THEN SUM(clm.PAID_AMOUNT) / COUNT(DISTINCT clm.ENCOUNTER_ID)
                    ELSE 0 END AS COST_PER_ENCOUNTER,
                grp.ENCOUNTER_GROUP,
                type.ENCOUNTER_TYPE
            FROM FACT_CLAIMS clm
            JOIN FACT_MEMBER_MONTHS mm
                ON clm.YEAR_MONTH = mm.YEAR_MONTH
            LEFT JOIN DIM_ENCOUNTER_GROUP grp
                ON clm.ENCOUNTER_GROUP_SK = grp.ENCOUNTER_GROUP_SK
            LEFT JOIN DIM_ENCOUNTER_TYPE type
                ON clm.ENCOUNTER_TYPE_SK = type.ENCOUNTER_TYPE_SK
            {filter_sql}
            GROUP BY clm.YEAR_MONTH
            ORDER BY clm.YEAR_MONTH
            """
        result = query_sqlite(query)
        if not result.empty:
            result["YEAR_MONTH"] = pd.to_datetime(result["YEAR_MONTH"].astype(str), format="%Y%m")
        else:
            return pd.DataFrame(columns=['YEAR_MONTH', 'TOTAL_PAID', 'ENCOUNTERS_COUNT', 'MEMBERS_COUNT', 'PMPM', 'PKPY', 'COST_PER_ENCOUNTER'])
        
        return result
        
    except Exception as e:
        print(f"Error in get_trends_data: {e}")
        return pd.DataFrame(columns=['YEAR_MONTH', 'TOTAL_PAID', 'ENCOUNTERS_COUNT', 'MEMBERS_COUNT', 'PMPM', 'PKPY', 'COST_PER_ENCOUNTER'])


@callback(
    Output("pmpm-trend", "figure"),
    Input("date-picker-input", "start_date"),
    Input("date-picker-input", "end_date"),
    Input("comparison-period-dropdown", "value"),
    Input("encounter-group-chart", "selectedData"),
    Input("encounter-type-chart", "selectedData"),

)
def update_pmpm_trend(start_date, end_date, comparison_period, group_click, encounter_type_click):
    filters = {}
    if group_click:
        filters["ENCOUNTER_GROUP"] = group_click["points"][0]["y"]
    
    if encounter_type_click:
        filters["ENCOUNTER_TYPE"] = encounter_type_click["points"][0]["y"]

    df = get_trends_data(filters)

    start = pd.to_datetime(start_date).replace(day=1)
    end = pd.to_datetime(end_date).replace(day=1)
    selected_months = pd.date_range(start=start, end=end, freq='MS')

    current_data = []
    if not df.empty:
        current_df = df[df["YEAR_MONTH"].isin(selected_months)]
        current_data = list(zip(current_df["YEAR_MONTH"], current_df["PMPM"]))

    comparison_data = []
    for month in selected_months:
        comp_range = get_comparison_offset(month, comparison_period, selected_months)
        comp_df = df[df["YEAR_MONTH"].isin(comp_range)]
        total_paid = comp_df["TOTAL_PAID"].sum()
        total_members = comp_df["MEMBERS_COUNT"].sum()
        avg_pmpm = total_paid / total_members if total_members > 0 else 0
        comparison_data.append((month, avg_pmpm))

    return trend_chart(current_data, comparison_data)

@callback(
    Output("pkpy-trend", "figure"),
    Input("date-picker-input", "start_date"),
    Input("date-picker-input", "end_date"),
    Input("comparison-period-dropdown", "value"),
    Input("encounter-group-chart", "selectedData"),
    Input("encounter-type-chart", "selectedData"),
)
def update_pkpy_trend(start_date, end_date, comparison_period, group_click, encounter_type_click):
    filters = {}
    if group_click:
        filters["ENCOUNTER_GROUP"] = group_click["points"][0]["y"]
 
    if encounter_type_click:
        filters["ENCOUNTER_TYPE"] = encounter_type_click["points"][0]["y"]

    df = get_trends_data(filters)

    start = pd.to_datetime(start_date).replace(day=1)
    end = pd.to_datetime(end_date).replace(day=1)
    selected_months = pd.date_range(start=start, end=end, freq='MS')

    current_data = []
    if not df.empty:
        current_df = df[df["YEAR_MONTH"].isin(selected_months)]
        current_data = list(zip(current_df["YEAR_MONTH"], current_df["PKPY"]))

    comparison_data = []
    for month in selected_months:
        comp_range = get_comparison_offset(month, comparison_period, selected_months)
        comp_df = df[df["YEAR_MONTH"].isin(comp_range)]
        total_encounters = comp_df["ENCOUNTERS_COUNT"].sum()
        total_members = comp_df["MEMBERS_COUNT"].sum()
        if total_members > 0:
            avg_pkpy = (total_encounters / total_members) * 12000
            comparison_data.append((month, avg_pkpy))

    return trend_chart(current_data, comparison_data)

@callback(
    Output("cost-per-trend", "figure"),
    Input("date-picker-input", "start_date"),
    Input("date-picker-input", "end_date"),
    Input("comparison-period-dropdown", "value"),
    Input("encounter-group-chart", "selectedData"),
    Input("encounter-type-chart", "selectedData"),
)
def update_cost_per_trend(start_date, end_date, comparison_period, group_click, encounter_type_click):
    filters = {}
    if group_click:
        filters["ENCOUNTER_GROUP"] = group_click["points"][0]["y"]
 
    if encounter_type_click:
        filters["ENCOUNTER_TYPE"] = encounter_type_click["points"][0]["y"]

    df = get_trends_data(filters)

    start = pd.to_datetime(start_date).replace(day=1)
    end = pd.to_datetime(end_date).replace(day=1)
    selected_months = pd.date_range(start=start, end=end, freq='MS')

    current_data = []
    if not df.empty:
        current_df = df[df["YEAR_MONTH"].isin(selected_months)]
        current_data = list(zip(current_df["YEAR_MONTH"], current_df["COST_PER_ENCOUNTER"]))

    comparison_data = []
    for month in selected_months:
        comp_range = get_comparison_offset(month, comparison_period, selected_months)
        comp_df = df[df["YEAR_MONTH"].isin(comp_range)]

        if not comp_df.empty:
            total_paid = comp_df["TOTAL_PAID"].sum()
            total_encounters = comp_df["ENCOUNTERS_COUNT"].sum()
            if total_encounters > 0:
                avg_cost_per_encounter = total_paid / total_encounters
                comparison_data.append((month, avg_cost_per_encounter))

    return trend_chart(current_data, comparison_data)