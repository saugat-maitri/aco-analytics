
from dash import Input, Output, callback
import pandas as pd
from datetime import datetime

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
                SUM(fc.PAID_AMOUNT) AS total_paid 
            FROM FACT_CLAIMS AS fc 
            WHERE fc.YEAR_MONTH BETWEEN {start_yyyymm} AND {end_yyyymm}
            GROUP BY fc.CCSR_CATEGORY_DESCRIPTION
        ),
        member_months_claims AS (
            SELECT COUNT(DISTINCT person_id || '-' || year_month) AS member_months_count
            FROM FACT_MEMBER_MONTHS 
            WHERE year_month BETWEEN {start_yyyymm} AND {end_yyyymm}
        )
        SELECT 
            CASE WHEN cc.CCSR_CATEGORY_DESCRIPTION IS NULL THEN 'Others' ELSE cc.CCSR_CATEGORY_DESCRIPTION END AS CCSR_CATEGORY_DESCRIPTION,
            cc.total_paid,
            CASE 
                WHEN mm.member_months_count > 0 
                THEN cc.total_paid / mm.member_months_count 
                ELSE 0 
            END AS pmpm
        FROM category_claims AS cc
        CROSS JOIN member_months_claims AS mm
        ORDER BY pmpm DESC
        """
        
        result = query_sqlite(query)
        
        # Ensure we always return a DataFrame, even if empty
        if result is None:
            return pd.DataFrame(columns=['CCSR_CATEGORY_DESCRIPTION', 'total_paid', 'pmpm'])
        
        return result
        
    except Exception as e:
        print(f"Error in get_condition_ccsr_data: {e}")
        return pd.DataFrame(columns=['CCSR_CATEGORY_DESCRIPTION', 'total_paid', 'pmpm'])

@callback(
    Output("condition-ccsr-cost-driver", "children"),
    Input("date-picker-input", "start_date"),
    Input("date-picker-input", "end_date"),
)
def update_condition_ccsr_cost_driver_graph(start_date, end_date):
    try:
        # Convert date strings to YYYYMM format for filtering
        start_yyyymm = dt_to_yyyymm(datetime.strptime(start_date, "%Y-%m-%d"))
        end_yyyymm = dt_to_yyyymm(datetime.strptime(end_date, "%Y-%m-%d"))
        
        ccsr_data = get_condition_ccsr_data(start_yyyymm, end_yyyymm)
        
        # Handle case where query returns None
        if ccsr_data is None:
            return "No data available for the selected period"
        
        if ccsr_data.empty:
            return "No data available for the selected period"
        
        # Rename columns to match component expectations
        ccsr_data = ccsr_data.rename(columns={
            'total_paid': 'TOTAL_PAID',
            'pmpm': 'PMPM'
        })
        
        return condition_ccsr_cost_driver_graph(ccsr_data)
    
    except Exception as e:
        print(f"Error in update_condition_ccsr_cost_driver_graph: {e}")
        return f"Error loading data: {str(e)}"