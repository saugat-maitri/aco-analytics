
from dash import Input, Output, callback
import pandas as pd
from functools import lru_cache
from typing import Tuple

from components import kpi_card
from data.db_query import query_sqlite
from utils import dt_to_yyyymm
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


@lru_cache(maxsize=2)
def load_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Load and cache claims and member data from Snowflake."""
    claims_query = "SELECT * FROM FACT_CLAIMS limit 1000"
    member_query = "SELECT * FROM FACT_MEMBER_MONTHS limit 1000"
    claims_agg = query_sqlite(claims_query)
    member_months = query_sqlite(member_query)
    claims_agg["YEAR_MONTH"] = claims_agg["YEAR_MONTH"].astype(int)
    member_months["YEAR_MONTH"] = member_months["YEAR_MONTH"].astype(int)

    return claims_agg, member_months

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

def calc_kpis(start_date, end_date):
    claims_agg, member_months = load_data()
    start_date = dt_to_yyyymm(start_date)
    end_date = dt_to_yyyymm(end_date)

    claims_agg_df = claims_agg[(claims_agg["YEAR_MONTH"] >= start_date) & (claims_agg["YEAR_MONTH"] <= end_date)]
    member_months_df = member_months[(member_months["YEAR_MONTH"] >= start_date) & (member_months["YEAR_MONTH"] <= end_date)]

    mm = member_months_df[["PERSON_ID", "YEAR_MONTH"]].drop_duplicates().shape[0]
    encounters = claims_agg_df["ENCOUNTER_ID"].nunique()
    paid = claims_agg_df["PAID_AMOUNT"].sum()
    pmpm = paid / mm if mm else 0
    utilization = (encounters / mm * 12000) if mm else 0
    cpe = paid / encounters if encounters else 0
    return pmpm, utilization, cpe

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
    Input("my-date-picker-range", "start_date"),
    Input("my-date-picker-range", "end_date"),
    Input("comparison-period-dropdown", "value")
)
def update_kpi_cards(start_date, end_date, comparison_period):
    start_main, end_main, start_comp, end_comp = get_comparison_period(start_date, end_date, comparison_period)

    pmpm_main, util_main, cpe_main = calc_kpis(start_main, end_main)
    pmpm_comp, util_comp, cpe_comp = calc_kpis(start_comp, end_comp)

    # Comparison values (dummy for now)
    expected = 300
    # Return dynamic cards
    return (
        kpi_card("PMPM Cost", pmpm_main, pmpm_comp, expected, "comparison-pmpm"),
        kpi_card("Utilization (PKPY)", util_main, util_comp, expected, "comparison-utilization"),
        kpi_card("Cost Per Encounter", cpe_main, cpe_comp, expected, "comparison-cost")
    )