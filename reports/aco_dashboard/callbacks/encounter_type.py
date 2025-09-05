from datetime import datetime

import pandas as pd
from dash import Input, Output, callback

from components.bar_chart import horizontal_bar_chart
from services.database import sqlite_manager
from services.utils import dt_to_yyyymm, extract_sql_filters


def get_encounter_type_pmpm_data(start_yyyymm, end_yyyymm, filters) -> pd.DataFrame:
    filter_sql = ""
    if filters:
        for col, value in filters.items():
            if value is not None:
                filter_sql += f" AND {col} = '{value}'"
    try:
        query = f"""
        WITH claims_by_encounter_type AS (
            SELECT
                typ.ENCOUNTER_TYPE,
                SUM(PAID_AMOUNT) as TOTAL_PAID
            FROM FACT_CLAIMS clm
            LEFT JOIN DIM_ENCOUNTER_TYPE typ
                ON clm.ENCOUNTER_TYPE_SK = typ.ENCOUNTER_TYPE_SK
            LEFT JOIN DIM_ENCOUNTER_GROUP grp
                ON clm.ENCOUNTER_GROUP_SK = grp.ENCOUNTER_GROUP_SK
            WHERE clm.YEAR_MONTH BETWEEN {start_yyyymm} AND {end_yyyymm}
            {filter_sql}
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
        result = sqlite_manager.query(query)
        # Ensure we always return a DataFrame, even if empty
        if result is None:
            return pd.DataFrame(columns=['ENCOUNTER_TYPE', 'PMPM'])
        
        return result
        
    except Exception as e:
        print(f"Error in get_encounter_type_pmpm_data: {e}")
        return pd.DataFrame(columns=['ENCOUNTER_TYPE', 'PMPM'])

@callback(
    Output("encounter-type-chart", "figure"),
    Input("date-picker-input", "start_date"),
    Input("date-picker-input", "end_date"),
    Input("encounter-group-chart", "selectedData"),
)
def update_encounter_type_pmpm_bar(start_date, end_date, group_click):
    try:
        # Convert date strings to YYYYMM format for filtering
        start_yyyymm = dt_to_yyyymm(datetime.strptime(start_date, "%Y-%m-%d"))
        end_yyyymm = dt_to_yyyymm(datetime.strptime(end_date, "%Y-%m-%d"))

        filters = extract_sql_filters(group_click)
        
        data = get_encounter_type_pmpm_data(start_yyyymm, end_yyyymm, filters)
        def color_fn(pmpm):
            return ['#ed3030' if val > 400 else '#428c8d' for val in pmpm]

        def text_fn(pmpm):
            return [f"${v:,.0f}" for v in pmpm]
        
        return horizontal_bar_chart(
            x=data["PMPM"],
            y=data["ENCOUNTER_TYPE"],
            color_fn=color_fn,
            text_fn=text_fn,
            margin=dict(l=20, r=20, t=20, b=20),
            showticklabels=False,
            customdata=data["ENCOUNTER_TYPE"],
            hovertemplate=('Encounter Type: %{customdata}<br>PMPM: %{text}<br><extra></extra>')
        )
    
    except Exception as e:
        print(f"Error in update_encounter_type_pmpm_bar: {e}")
        return f"Error loading data: {str(e)}"