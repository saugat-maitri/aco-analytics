from datetime import datetime

import pandas as pd
from dash import Input, Output, callback

from components.bar_chart import horizontal_bar_chart
from services.database import sqlite_manager
from services.utils import dt_to_yyyymm, truncate_text


def get_condition_ccsr_data(start_yyyymm: int, end_yyyymm: int) -> pd.DataFrame:
    """Load condition CCSR data using efficient CTE-based query."""
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

    return sqlite_manager.query(query)


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

        ccsr_data["TRUNCATED_CATEGORY"] = ccsr_data["CCSR_CATEGORY_DESCRIPTION"].apply(
            lambda x: truncate_text(x, 30)
        )
        return horizontal_bar_chart(
            data=ccsr_data,
            x="PMPM",
            y="TRUNCATED_CATEGORY",
            text_fn=[f"${v:,.0f}" for v in ccsr_data["PMPM"]],
            marker_color="#64AFE0",
            margin=dict(l=20, r=20, t=20, b=0),
            showticklabels=False,
            customdata=ccsr_data["CCSR_CATEGORY_DESCRIPTION"],
            hovertemplate=(
                "CCSR Category: %{customdata}<br>PMPM: %{text}<br><extra></extra>"
            ),
        )

    except Exception as e:
        print(f"Error in update_condition_ccsr_cost_driver_graph: {e}")
        return f"Error loading data: {str(e)}"
