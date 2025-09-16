from datetime import datetime, timedelta
from typing import Tuple

import pandas as pd
from dateutil.relativedelta import relativedelta
from pandas import DateOffset


def dt_to_yyyymm(dt):
    return dt.year * 100 + dt.month


def extract_sql_filters(group_click=None, encounter_type_click=None, ccsr_click=None):
    """Extract SQL filters from the selected data points."""
    filters = {}
    if group_click and group_click.get("points"):
        filters["ENCOUNTER_GROUP"] = group_click["points"][0]["y"]
    if encounter_type_click and encounter_type_click.get("points"):
        filters["ENCOUNTER_TYPE"] = encounter_type_click["points"][0]["y"]
    if ccsr_click and ccsr_click.get("points"):
        filters["CCSR_CATEGORY_DESCRIPTION"] = ccsr_click["points"][0]["customdata"]
    return filters


# Truncate long text
def truncate_text(text, max_length=30):
    return text[:max_length] + "..." if len(text) > max_length else text

def format_large_number(value):
    """Format large numbers with commas and add $ as prefix."""
    if value >= 1_000_000_000:
        return f"${value / 1_000_000_000:.0f}B"
    elif value >= 1_000_000:
        return f"${value / 1_000_000:.0f}M"
    elif value >= 1_000:
        return f"${value / 1_000:.0f}K"
    else:
        return f"${value:.2f}"


def get_comparison_period(
    start: datetime, end: datetime, comparison_period: str
) -> Tuple[datetime, datetime]:
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
    return comp_start, comp_end


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

    return pd.date_range(start=comp_start, end=comp_end, freq="MS")
