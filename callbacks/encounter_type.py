
from dash import Input, Output, callback
import pandas as pd
from datetime import datetime

from components import encounter_type_pmpm_bar, pmpm_vs_expected_bar
from data.db_query import query_sqlite
from utils import dt_to_yyyymm

def get_encounter_type_pmpm_data(start_yyyymm: int, end_yyyymm: int) -> pd.DataFrame:
    try:
        query = f"""
        WITH claims_by_encounter_type AS (
            SELECT
                typ.ENCOUNTER_TYPE,
                SUM(PAID_AMOUNT) as TOTAL_PAID
            FROM FACT_CLAIMS clm
            LEFT JOIN DIM_ENCOUNTER_TYPE typ
                ON clm.ENCOUNTER_TYPE_SK = typ.ENCOUNTER_TYPE_SK
            WHERE clm.YEAR_MONTH BETWEEN {start_yyyymm} AND {end_yyyymm}
            GROUP BY typ.ENCOUNTER_TYPE
        ),
        member_months AS (
            SELECT COUNT(DISTINCT PERSON_ID || '-' || YEAR_MONTH) AS MEMBER_MONTHS_COUNT
            FROM FACT_MEMBER_MONTHS
            WHERE year_month BETWEEN {start_yyyymm} AND {end_yyyymm}
        )

        SELECT
            clm.ENCOUNTER_TYPE,
            CASE 
                WHEN mm.MEMBER_MONTHS_COUNT > 0 
                THEN clm.TOTAL_PAID / mm.MEMBER_MONTHS_COUNT 
                ELSE 0 
            END AS PMPM
        FROM claims_by_encounter_type clm
        CROSS JOIN member_months AS MM
        ORDER BY PMPM DESC
        """
        result = query_sqlite(query)
        # Ensure we always return a DataFrame, even if empty
        if result is None:
            return pd.DataFrame(columns=['ENCOUNTER_TYPE', 'PMPM'])
        
        return result
        
    except Exception as e:
        print(f"Error in get_encounter_type_pmpm_data: {e}")
        return pd.DataFrame(columns=['ENCOUNTER_TYPE', 'PMPM'])

@callback(
    Output("encounter-type-bar", "figure"),
    Input("date-picker-input", "start_date"),
    Input("date-picker-input", "end_date"),
)
def update_encounter_type_pmpm_bar(start_date, end_date):
    try:
        # Convert date strings to YYYYMM format for filtering
        start_yyyymm = dt_to_yyyymm(datetime.strptime(start_date, "%Y-%m-%d"))
        end_yyyymm = dt_to_yyyymm(datetime.strptime(end_date, "%Y-%m-%d"))
        
        data = get_encounter_type_pmpm_data(start_yyyymm, end_yyyymm)
        
        # Handle case where query returns None
        if data is None or data.empty:
            return "No data available for the selected period"
        
        return encounter_type_pmpm_bar(data)
    
    except Exception as e:
        print(f"Error in update_encounter_type_pmpm_bar: {e}")
        return f"Error loading data: {str(e)}"