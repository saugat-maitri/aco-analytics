
from datetime import datetime

import pandas as pd
from dash import Input, Output, callback

from components import pmpm_vs_expected_bar
from data.db_query import query_sqlite
from utils import dt_to_yyyymm


def get_pmpm_performance_vs_expected_data(start_yyyymm: int, end_yyyymm: int) -> pd.DataFrame:
    try:
        query = f"""
        WITH claims_by_encounter_group AS (
            SELECT
                grp.ENCOUNTER_GROUP,
                SUM(PAID_AMOUNT) as TOTAL_PAID
            FROM FACT_CLAIMS clm
            LEFT JOIN DIM_ENCOUNTER_GROUP grp
                ON clm.ENCOUNTER_GROUP_SK = grp.ENCOUNTER_GROUP_SK
            WHERE clm.YEAR_MONTH BETWEEN {start_yyyymm} AND {end_yyyymm}
            GROUP BY grp.ENCOUNTER_GROUP
        ),
        member_months AS (
            SELECT COUNT(DISTINCT PERSON_ID || '-' || YEAR_MONTH) AS MEMBER_MONTHS_COUNT
            FROM FACT_MEMBER_MONTHS
            WHERE year_month BETWEEN {start_yyyymm} AND {end_yyyymm}
        )

        SELECT
            clm.ENCOUNTER_GROUP,
            CASE 
                WHEN mm.MEMBER_MONTHS_COUNT > 0 
                THEN clm.TOTAL_PAID / mm.MEMBER_MONTHS_COUNT 
                ELSE 0 
            END AS PMPM
        FROM claims_by_encounter_group clm
        CROSS JOIN member_months AS MM
        ORDER BY PMPM DESC
        """
        result = query_sqlite(query)
        # Ensure we always return a DataFrame, even if empty
        if result is None:
            return pd.DataFrame(columns=['ENCOUNTER_GROUP', 'PMPM'])
        
        return result
        
    except Exception as e:
        print(f"Error in get_pmpm_performance_vs_expected_data: {e}")
        return pd.DataFrame(columns=['ENCOUNTER_GROUP', 'PMPM'])

@callback(
    Output("encounter-group-chart", "figure"),
    Input("date-picker-input", "start_date"),
    Input("date-picker-input", "end_date"),
)
def update_pmpm_performance_vs_expected(start_date, end_date):
    try:
        # Convert date strings to YYYYMM format for filtering
        start_yyyymm = dt_to_yyyymm(datetime.strptime(start_date, "%Y-%m-%d"))
        end_yyyymm = dt_to_yyyymm(datetime.strptime(end_date, "%Y-%m-%d"))
        
        data = get_pmpm_performance_vs_expected_data(start_yyyymm, end_yyyymm)
        
        return pmpm_vs_expected_bar(data)
    
    except Exception as e:
        print(f"Error in update_pmpm_performance_vs_expected: {e}")
        return f"Error loading data: {str(e)}"