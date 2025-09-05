from datetime import datetime

import pandas as pd
from dash import Input, Output, callback

from components.box_plot import box_plot
from components.demographics_card import demographics_card
from components.no_data_figure import no_data_figure
from services.database import sqlite_manager
from services.utils import dt_to_yyyymm


def get_demographic_data(start_yyyymm: int, end_yyyymm: int) -> pd.DataFrame:
    try:
        query = f"""
        WITH member_month_details AS (
            SELECT 
                f.PERSON_ID,
                f.YEAR_MONTH,
                d.SEX,
                d.AGE,
                f.NORMALIZED_RISK_SCORE,
                CAST(f.PERSON_ID AS TEXT) || '-' || CAST(f.YEAR_MONTH AS TEXT) AS MEMBER_MONTH_ID
            FROM FACT_MEMBER_MONTHS AS f
            LEFT JOIN DIM_MEMBER AS d
                ON f.PERSON_ID = d.PERSON_ID
            WHERE f.YEAR_MONTH BETWEEN {start_yyyymm} AND {end_yyyymm}
        ),
        member_month_counts AS (
            SELECT
                COUNT(DISTINCT MEMBER_MONTH_ID) AS TOTAL_MEMBER_MONTHS,
                COUNT(DISTINCT YEAR_MONTH) AS TOTAL_MONTHS
            FROM member_month_details
        )
        SELECT 
            mmc.TOTAL_MEMBER_MONTHS,
            mmc.TOTAL_MEMBER_MONTHS * 1.0 / mmc.TOTAL_MONTHS AS AVG_MEMBERS_PER_MONTH,
            AVG(mmd.AGE) AS AVG_AGE,
            100.0 * SUM(CASE WHEN LOWER(mmd.SEX) = 'female' THEN 1 ELSE 0 END) 
                / mmc.TOTAL_MEMBER_MONTHS AS PERCENT_FEMALE,
            AVG(mmd.NORMALIZED_RISK_SCORE) AS AVG_RISK_SCORE
        FROM member_month_details mmd
        CROSS JOIN member_month_counts mmc;
        """
        result = sqlite_manager.query(query)
        return result
        
    except Exception as e:
        print(f"Error in get_demographic_data: {e}")
        return pd.DataFrame(columns=['TOTAL_MEMBER_MONTHS', 'AVG_MEMBERS_PER_MONTH', 'AVG_AGE', 'PERCENT_FEMALE', 'AVG_RISK_SCORE'])
    

def get_risk_distribution_data(start_yyyymm: int, end_yyyymm: int) -> pd.DataFrame | None:
    """Fetch risk distribution data between start_yyyymm and end_yyyymm.
    
    Returns:
        - DataFrame if query succeeds
        - None if query fails
    """
    query = f"""
        SELECT 
            NORMALIZED_RISK_SCORE
        FROM fact_member_monthss
        WHERE YEAR_MONTH BETWEEN '{start_yyyymm}' AND '{end_yyyymm}'
    """
    result = sqlite_manager.query(query)

    # Return DataFrame even if empty
    return result



@callback(
    Output("demographic-card", "children"),
    Input("date-picker-input", "start_date"),
    Input("date-picker-input", "end_date"),
)
def update_demographic_data(start_date, end_date):
    try:
        # Convert date strings to YYYYMM format for filtering
        start_yyyymm = dt_to_yyyymm(datetime.strptime(start_date, "%Y-%m-%d"))
        end_yyyymm = dt_to_yyyymm(datetime.strptime(end_date, "%Y-%m-%d"))
        
        demographic_data = get_demographic_data(start_yyyymm, end_yyyymm)
        return demographics_card(demographic_data)
    
    except Exception as e:
        print(f"Error in update_demographic_data: {e}")
        return no_data_figure(message=f"Error loading data: {str(e)}")
    
@callback(
    Output("risk-distribution-card", "figure"),
    Input("date-picker-input", "start_date"),
    Input("date-picker-input", "end_date"),
)
def update_risk_data(start_date: str, end_date: str):
    """Prepare risk distribution visualization for given date range."""
    try:
        # Convert date strings to YYYYMM format
        start_yyyymm = dt_to_yyyymm(datetime.strptime(start_date, "%Y-%m-%d"))
        end_yyyymm = dt_to_yyyymm(datetime.strptime(end_date, "%Y-%m-%d"))
        
        # Fetch data
        risk_data = get_risk_distribution_data(start_yyyymm, end_yyyymm)

        fig = box_plot(
            data=risk_data,
            y="NORMALIZED_RISK_SCORE",
            points="outliers",
            show_line=True,
        )
        return fig

    except Exception as e:
        print(f"Error in update_risk_data: {e}")
        return no_data_figure(message=f"Error loading data: {str(e)}")