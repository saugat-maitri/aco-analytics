import pandas as pd
from functools import lru_cache
from typing import Tuple
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
