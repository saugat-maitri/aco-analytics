
from datetime import datetime

import pandas as pd
from dash import Input, Output, callback

from components import condition_ccsr_cost_driver_graph
from data.db_query import query_sqlite
from utils import dt_to_yyyymm


def get_condition_ccsr_data(start_yyyymm: int, end_yyyymm: int) -> pd.DataFrame:
    """Load condition CCSR data using efficient CTE-based query."""
    try:
        query = f"""
        WITH
        category_claims AS (
            SELECT 
                fc.CCSR_CATEGORY_DESCRIPTION, 
                SUM(fc.PAID_AMOUNT) AS TOTAL_PAID 
            FROM FACT_CLAIMS AS fc 
            WHERE fc.YEAR_MONTH BETWEEN {start_yyyymm} AND {end_yyyymm}
            GROUP BY fc.CCSR_CATEGORY_DESCRIPTION
        ),
        member_months AS (
            SELECT COUNT(DISTINCT PERSON_ID || '-' || YEAR_MONTH) AS member_months_count
            FROM FACT_MEMBER_MONTHS 
            WHERE YEAR_MONTH BETWEEN {start_yyyymm} AND {end_yyyymm}
        )
        SELECT 
            CASE WHEN cc.CCSR_CATEGORY_DESCRIPTION IS NULL THEN 'Others' ELSE cc.CCSR_CATEGORY_DESCRIPTION END AS CCSR_CATEGORY_DESCRIPTION,
            cc.TOTAL_PAID,
            CASE 
                WHEN mm.MEMBER_MONTHS_COUNT > 0 
                THEN cc.TOTAL_PAID / mm.MEMBER_MONTHS_COUNT 
                ELSE 0 
            END AS PMPM
        FROM category_claims AS cc
        CROSS JOIN member_months AS mm
        ORDER BY PMPM DESC
        """
        
        result = query_sqlite(query)
        
        # Ensure we always return a DataFrame, even if empty
        if result is None:
            return pd.DataFrame(columns=['CCSR_CATEGORY_DESCRIPTION', 'TOTAL_PAID', 'PMPM'])
        
        return result
        
    except Exception as e:
        print(f"Error in get_condition_ccsr_data: {e}")
        return pd.DataFrame(columns=['CCSR_CATEGORY_DESCRIPTION', 'TOTAL_PAID', 'PMPM'])

@callback(
    Output("condition-ccsr-chart", "figure"),
    Input("date-picker-input", "start_date"),
    Input("date-picker-input", "end_date"),
)
def update_condition_ccsr_cost_driver_graph(start_date, end_date):
    try:
        # Convert date strings to YYYYMM format for filtering
        start_yyyymm = dt_to_yyyymm(datetime.strptime(start_date, "%Y-%m-%d"))
        end_yyyymm = dt_to_yyyymm(datetime.strptime(end_date, "%Y-%m-%d"))
        
        ccsr_data = get_condition_ccsr_data(start_yyyymm, end_yyyymm)
        
        return condition_ccsr_cost_driver_graph(ccsr_data)
    
    except Exception as e:
        print(f"Error in update_condition_ccsr_cost_driver_graph: {e}")
        return f"Error loading data: {str(e)}"