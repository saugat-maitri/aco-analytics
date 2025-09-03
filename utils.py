from functools import lru_cache
from typing import Tuple

import pandas as pd

from data.db_query import query_sqlite


def dt_to_yyyymm(dt):
    return dt.year * 100 + dt.month

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
    return text[:max_length] + '...' if len(text) > max_length else text
