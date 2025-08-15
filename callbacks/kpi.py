
from dash import Input, Output, callback

from components import kpi_card
from data.db_query import query_sqlite
from utils import dt_to_yyyymm
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


def get_comparison_period(start_date_str, end_date_str, comparison_period):
    start = datetime.strptime(start_date_str, "%Y-%m-%d")
    end = datetime.strptime(end_date_str, "%Y-%m-%d")
    period_months = (end.year - start.year) * 12 + (end.month - start.month) + 1

    if comparison_period == "Same Period Last Year":
        comp_start = start.replace(year=start.year - 1)
        comp_end = end.replace(year=end.year - 1)

    elif comparison_period == "Previous Year":
        comp_start = datetime(start.year - 1, 1, 1)
        comp_end = datetime(start.year - 1, 12, 31)

    elif comparison_period == "Previous Period":
        comp_end = start - timedelta(days=1)
        comp_start = comp_end - relativedelta(months=period_months - 1)
        comp_start = comp_start.replace(day=1)

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

    return start, end, comp_start, comp_end

def calc_kpis(start_date, end_date, filters=None):
    start_date = dt_to_yyyymm(start_date)
    end_date = dt_to_yyyymm(end_date)

    filter_sql = ""
    if filters:
        for col, value in filters.items():
            if value is not None:
                filter_sql += f" AND {col} = '{value}'"

    query = f"""
    WITH claims_agg AS (
        SELECT
            SUM(PAID_AMOUNT) AS paid,
            COUNT(DISTINCT ENCOUNTER_ID) AS encounters
        FROM FACT_CLAIMS clm
        LEFT JOIN DIM_ENCOUNTER_GROUP grp
            ON clm.ENCOUNTER_GROUP_SK = grp.ENCOUNTER_GROUP_SK
        LEFT JOIN DIM_ENCOUNTER_TYPE type
            ON clm.ENCOUNTER_TYPE_SK = type.ENCOUNTER_TYPE_SK
        WHERE YEAR_MONTH BETWEEN {start_date} AND {end_date}
        {filter_sql}
    ),
    member_months AS (
        SELECT COUNT(DISTINCT PERSON_ID || '-' || YEAR_MONTH) AS mm
        FROM FACT_MEMBER_MONTHS
        WHERE YEAR_MONTH BETWEEN {start_date} AND {end_date}
    )
    SELECT
        claims_agg.paid,
        claims_agg.encounters,
        member_months.mm
    FROM claims_agg, member_months
    """
    result = query_sqlite(query)
    if result is None or result.empty:
        return 0, 0, 0
    paid = result.iloc[0]["paid"] or 0
    encounters = result.iloc[0]["encounters"] or 0
    mm = result.iloc[0]["mm"] or 0
    pmpm = paid / mm if mm else 0
    return pmpm

@callback(
    Output("comparison-pmpm", "children"),
    Input("comparison-period-dropdown", "value")
)
def update_comparison_text(comparison_period):
    return comparison_period

@callback(
    Output("pmpm-cost-card", "children"),
    Input("date-picker-input", "start_date"),
    Input("date-picker-input", "end_date"),
    Input("comparison-period-dropdown", "value"),
    Input("encounter-group-chart", "selectedData"),
    Input("encounter-type-chart", "selectedData"),
)
def update_kpi_cards(start_date, end_date, comparison_period, group_click, type_click):
    start_main, end_main, start_comp, end_comp = get_comparison_period(start_date, end_date, comparison_period)

    filters = {}
    if group_click:
        filters["ENCOUNTER_GROUP"] = group_click["points"][0]["y"]
    if type_click:
        filters["ENCOUNTER_TYPE"] = type_click["points"][0]["y"]

    pmpm_main = calc_kpis(start_main, end_main, filters)
    pmpm_comp = calc_kpis(start_comp, end_comp, filters)


    # Comparison values (dummy for now)
    expected = 300
    # Return dynamic cards
    return (
        kpi_card("PMPM Cost", pmpm_main, pmpm_comp, expected, "comparison-pmpm"),
    )