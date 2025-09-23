from datetime import datetime, timedelta
from typing import Optional, Tuple

import pandas as pd
from dateutil.relativedelta import relativedelta
from pandas import DateOffset


def dt_to_yyyymm(dt):
    """Convert a datetime object to an integer in YYYYMM format.

    Args:
        dt (datetime): The datetime object to convert.

    Returns:
        int: The date in YYYYMM integer format.
    """
    return dt.year * 100 + dt.month


def extract_sql_filters(group_click=None, encounter_type_click=None, ccsr_click=None):
    """Extract SQL filter values from selected data points in interactive charts.

    Args:
        group_click (dict, optional): Click data for encounter group selection.
        encounter_type_click (dict, optional): Click data for encounter type selection.
        ccsr_click (dict, optional): Click data for CCSR category selection.

    Returns:
        dict: Dictionary of SQL filter column names and their selected values.
    """
    filters = {}
    if group_click:
        filters["ENCOUNTER_GROUP"] = group_click
    if encounter_type_click and encounter_type_click.get("points"):
        filters["ENCOUNTER_TYPE"] = encounter_type_click["points"][0]["y"]
    if ccsr_click and ccsr_click.get("points"):
        ccsr_data = ccsr_click["points"][0]["customdata"]
        filters["CCSR_CATEGORY_DESCRIPTION"] = (
            ccsr_data if ccsr_data != "other" else None
        )
    return filters


def build_filter_clause(filters: Optional[dict]) -> tuple[str, list]:
    """Build a SQL filter condition string and parameter list from a dictionary of filters.

    Args:
        filters (dict, optional): Dictionary of column-value pairs for filtering.

    Returns:
        tuple[str, list]: Tuple containing the SQL condition string and a list of parameter values.
    """
    clauses = []
    params = []
    if not filters:
        return "", []

    for col, value in filters.items():
        if value is None:
            clauses.append(f"{col} IS NULL")
        else:
            clauses.append(f"{col} = ?")
            params.append(value)

    condition = " AND ".join(clauses)
    return (condition if condition else ""), params


def truncate_text(text, max_length=30):
    """Truncate a string to a maximum length, appending '...' if truncated.

    Args:
        text (str): The text to truncate.
        max_length (int, optional): Maximum allowed length. Defaults to 30.

    Returns:
        str: Truncated text with ellipsis if needed.
    """
    return text[:max_length] + "..." if len(text) > max_length else text


def format_large_number(value):
    """Format a numeric value with a dollar sign and appropriate suffix (B, M, K).

    Args:
        value (float): The number to format.

    Returns:
        str: Formatted string with dollar sign and suffix.

    Examples:
            - 1234567890 -> "$1B"
            - 1234567 -> "$1M"
            - 1234 -> "$1K"
            - 123.45 -> "$123.45"
    """
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
    """Calculate the start and end dates for a comparison period based on the selected period and comparison type.

    Args:
        start (datetime): Start date of the selected period.
        end (datetime): End date of the selected period.
        comparison_period (str): Type of comparison period (e.g., 'Same Period Last Year', 'Previous Year').

    Returns:
        tuple[datetime, datetime]: Start and end dates for the comparison period.
    """
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
    """Generate a date range for the comparison period based on the selected month and comparison type.

    Args:
        month (pd.Timestamp): The reference month for comparison.
        comparison_period (str): Type of comparison period (e.g., 'Previous Month', 'Previous Year').
        selected_months (list, optional): List of selected months for 'Previous Period' comparison.

    Returns:
        pd.DatetimeIndex: Range of months for the comparison period.
    """
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
