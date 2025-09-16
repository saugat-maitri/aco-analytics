from datetime import datetime
from typing import Optional

import pandas as pd

from services.database import sqlite_manager
from services.utils import dt_to_yyyymm


def calc_kpis(
    start_date: datetime, end_date: datetime, filters: Optional[dict] = None
) -> float:
    start_yyyymm = dt_to_yyyymm(start_date)
    end_yyyymm = dt_to_yyyymm(end_date)

    filter_sql = ""
    if filters:
        for col, value in filters.items():
            if value is not None:
                filter_sql += f" AND {col} = '{value}'"

    query = f"""
        WITH claims_agg AS (
            SELECT
                SUM(PAID_AMOUNT) AS paid,
                COUNT(DISTINCT ENCOUNTER_ID) AS encounters
            FROM FACT_CLAIMS clm
            LEFT JOIN DIM_ENCOUNTER_GROUP grp
                ON clm.ENCOUNTER_GROUP_SK = grp.ENCOUNTER_GROUP_SK
            LEFT JOIN DIM_ENCOUNTER_TYPE type
                ON clm.ENCOUNTER_TYPE_SK = type.ENCOUNTER_TYPE_SK
            WHERE YEAR_MONTH BETWEEN {start_yyyymm} AND {end_yyyymm}
            {filter_sql}
        ),
        member_months AS (
            SELECT COUNT(DISTINCT PERSON_ID || '-' || YEAR_MONTH) AS mm
            FROM FACT_MEMBER_MONTHS
            WHERE YEAR_MONTH BETWEEN {start_yyyymm} AND {end_yyyymm}
        )
        SELECT
            claims_agg.paid,
            claims_agg.encounters,
            member_months.mm
        FROM claims_agg, member_months
    """
    result = sqlite_manager.query(query)
    row = result.iloc[0]
    paid = row.get("paid") or 0
    mm = row.get("mm") or 0
    if mm:
        return paid / mm
    return 0


def get_demographic_data(start_yyyymm: int, end_yyyymm: int) -> pd.DataFrame:
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
    return sqlite_manager.query(query)


def get_risk_distribution_data(start_yyyymm: int, end_yyyymm: int) -> pd.DataFrame:
    """Fetch risk distribution data between start_yyyymm and end_yyyymm.

    Returns:
        - DataFrame if query succeeds
        - None if query fails
    """
    query = f"""
        SELECT 
            NORMALIZED_RISK_SCORE
        FROM fact_member_months
        WHERE YEAR_MONTH BETWEEN '{start_yyyymm}' AND '{end_yyyymm}'
    """
    return sqlite_manager.query(query)


def get_trends_data(filters) -> pd.DataFrame:
    filter_sql = ""
    if filters:
        filter_clauses = []
        for col, value in filters.items():
            if value is not None:
                filter_clauses.append(f"{col} = '{value}'")
        if filter_clauses:
            filter_sql = " WHERE " + " AND ".join(filter_clauses)

    query = f"""
        WITH member_counts_by_month AS (
            SELECT 
                YEAR_MONTH,
                COUNT(DISTINCT PERSON_ID) AS MEMBERS_COUNT
            FROM FACT_MEMBER_MONTHS
            GROUP BY YEAR_MONTH
        ),
        claim_aggregates_by_month AS (
            SELECT 
                clm.YEAR_MONTH,
                COUNT(DISTINCT clm.ENCOUNTER_ID) AS ENCOUNTERS_COUNT,
                SUM(clm.PAID_AMOUNT) AS TOTAL_PAID
            FROM FACT_CLAIMS clm
            LEFT JOIN DIM_ENCOUNTER_GROUP grp
                ON clm.ENCOUNTER_GROUP_SK = grp.ENCOUNTER_GROUP_SK
            LEFT JOIN DIM_ENCOUNTER_TYPE type
                ON clm.ENCOUNTER_TYPE_SK = type.ENCOUNTER_TYPE_SK
            {filter_sql}
            GROUP BY clm.YEAR_MONTH
        )
        SELECT 
            m.YEAR_MONTH,
            m.MEMBERS_COUNT,
            e.ENCOUNTERS_COUNT,
            e.TOTAL_PAID,

            CASE WHEN m.MEMBERS_COUNT > 0
                THEN COALESCE(e.TOTAL_PAID, 0) / m.MEMBERS_COUNT
                ELSE 0 END AS PMPM,

            CASE WHEN m.MEMBERS_COUNT > 0
                THEN COALESCE(e.ENCOUNTERS_COUNT, 0) * 12000 / m.MEMBERS_COUNT
                ELSE 0 END AS PKPY,

            CASE WHEN e.ENCOUNTERS_COUNT > 0
                THEN COALESCE(e.TOTAL_PAID, 0) / e.ENCOUNTERS_COUNT
                ELSE 0 END AS COST_PER_ENCOUNTER

        FROM member_counts_by_month m
        LEFT JOIN claim_aggregates_by_month e
            ON m.YEAR_MONTH = e.YEAR_MONTH
        ORDER BY m.YEAR_MONTH;
    """
    return sqlite_manager.query(query)


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


def get_pmpm_performance_vs_expected_data(
    start_yyyymm: int, end_yyyymm: int
) -> pd.DataFrame:
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
    return sqlite_manager.query(query)


def get_encounter_type_pmpm_data(start_yyyymm, end_yyyymm, filters) -> pd.DataFrame:
    filter_sql = ""
    if filters:
        for col, value in filters.items():
            if value is not None:
                filter_sql += f" AND {col} = '{value}'"

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
    return sqlite_manager.query(query)


def get_cohort_data(start_yyyymm, end_yyyymm, filters) -> pd.DataFrame:
    filter_sql = ""
    if filters:
        for col, value in filters.items():
            if value is not None:
                filter_sql += f" AND {col} = '{value}'"
    query = f"""
        WITH member_totals AS (
            SELECT 
                person_id,
                SUM(fc.PAID_AMOUNT) AS total_paid
            FROM fact_claims fc
            LEFT JOIN DIM_ENCOUNTER_GROUP grp
                ON fc.ENCOUNTER_GROUP_SK = grp.ENCOUNTER_GROUP_SK
            WHERE year_month BETWEEN {start_yyyymm} AND {end_yyyymm}
            {filter_sql}
            GROUP BY person_id
        ),

        total_person_count AS (
            SELECT COUNT(*) AS total_person_count
            FROM member_totals
        ),

        ranked_members AS (
            SELECT
                mt.person_id,
                mt.total_paid,
                ROW_NUMBER() OVER(ORDER BY mt.total_paid DESC) AS rn,
                tpc.total_person_count
            FROM member_totals mt
            CROSS JOIN total_person_count tpc
        ),

        group_summary AS (
            SELECT
                SUM(CASE WHEN rn <= CEIL(total_person_count * 0.01) THEN total_paid END) AS top_1_total,
                COUNT(CASE WHEN rn <= CEIL(total_person_count * 0.01) THEN 1 END) AS top_1_count,

                SUM(CASE WHEN rn <= CEIL(total_person_count * 0.05) THEN total_paid END) AS top_5_total,
                COUNT(CASE WHEN rn <= CEIL(total_person_count * 0.05) THEN 1 END) AS top_5_count,

                SUM(CASE WHEN rn <= CEIL(total_person_count * 0.20) THEN total_paid END) AS top_20_total,
                COUNT(CASE WHEN rn <= CEIL(total_person_count * 0.20) THEN 1 END) AS top_20_count,

                SUM(total_paid) AS all_total,
                COUNT(*) AS all_count
            FROM ranked_members
        )
        
        SELECT
            'Top 1%' AS percent_group,
            top_1_total AS total_paid_amount,
            top_1_count AS member_count,
            ROUND(100.0 * top_1_total / all_total, 2) AS percent_of_total
        FROM group_summary 
        UNION ALL
        SELECT
            'Top 5%' AS percent_group,
            top_5_total AS total_paid_amount,
            top_5_count AS member_count,
            ROUND(100.0 * top_5_total / all_total, 2) AS percent_of_total
        FROM group_summary
        UNION ALL
        SELECT
            'Top 20%' AS percent_group,
            top_20_total AS total_paid_amount,
            top_20_count AS member_count,
            ROUND(100.0 * top_20_total / all_total, 2) AS percent_of_total
        FROM group_summary
        UNION ALL
        SELECT
            'All Members' AS percent_group,
            all_total AS total_paid_amount,
            all_count AS member_count,
            100.0 AS percent_of_total
        FROM group_summary
    """
    return sqlite_manager.query(query)