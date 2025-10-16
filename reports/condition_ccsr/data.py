from typing import Optional

import pandas as pd

from services.database import sqlite_manager
from services.utils import build_filter_clause


def get_ccsr_metrics_data(
    start_yyyymm: int, end_yyyymm: int, filters: Optional[dict] = None
) -> pd.DataFrame:
    filter_clause, params = build_filter_clause(filters)
    if filter_clause:
        filter_clause = f" AND {filter_clause}"
    query = f"""
        WITH
        category_claims AS (
            SELECT 
                fc.CCSR_CATEGORY_DESCRIPTION, 
                SUM(fc.PAID_AMOUNT) AS TOTAL_PAID,
                COUNT(DISTINCT fc.ENCOUNTER_ID) as ENCOUNTER_COUNT
            FROM FACT_CLAIMS AS fc 
            LEFT JOIN DIM_ENCOUNTER_GROUP grp
                ON fc.ENCOUNTER_GROUP_SK = grp.ENCOUNTER_GROUP_SK
            WHERE fc.YEAR_MONTH BETWEEN {start_yyyymm} AND {end_yyyymm}
            {filter_clause}
            GROUP BY fc.CCSR_CATEGORY_DESCRIPTION
        ),
        member_months AS (
            SELECT 
                COUNT(DISTINCT PERSON_ID || '-' || YEAR_MONTH) AS member_months_count,
                COUNT(DISTINCT PERSON_ID) as total_members
            FROM FACT_MEMBER_MONTHS 
            WHERE YEAR_MONTH BETWEEN {start_yyyymm} AND {end_yyyymm}
        )
        SELECT 
            CASE WHEN cc.CCSR_CATEGORY_DESCRIPTION IS NULL THEN 'other' ELSE cc.CCSR_CATEGORY_DESCRIPTION END AS CCSR_CATEGORY_DESCRIPTION,
            cc.TOTAL_PAID,
            mm.total_members,
            CASE 
                WHEN mm.MEMBER_MONTHS_COUNT > 0 
                THEN cc.TOTAL_PAID / mm.MEMBER_MONTHS_COUNT 
                ELSE 0 
            END AS PMPM,
            CASE 
                WHEN cc.ENCOUNTER_COUNT > 0 
                THEN cc.TOTAL_PAID / cc.ENCOUNTER_COUNT 
                ELSE 0 
            END AS COST_PER_ENCOUNTER,
            CASE 
                WHEN mm.total_members > 0 
                THEN cc.ENCOUNTER_COUNT * 12000 / mm.total_members 
                ELSE 0 
            END AS PKPY
        FROM category_claims AS cc
        CROSS JOIN member_months AS mm
        ORDER BY PMPM DESC;
    """
    return sqlite_manager.query(query, params)


def get_pmpm_by_encounter_type_data(
    start_yyyymm: int, end_yyyymm: int, filters: Optional[dict] = None
) -> pd.DataFrame:
    filter_clause, params = build_filter_clause(filters)
    if filter_clause:
        filter_clause = f" AND {filter_clause}"
    query = f"""
         WITH claims_by_encounter_type AS (
            SELECT
                typ.ENCOUNTER_TYPE,
                SUM(PAID_AMOUNT) as TOTAL_PAID
            FROM FACT_CLAIMS clm
            LEFT JOIN DIM_ENCOUNTER_TYPE typ
                ON clm.ENCOUNTER_TYPE_SK = typ.ENCOUNTER_TYPE_SK
            WHERE clm.YEAR_MONTH BETWEEN {start_yyyymm} AND {end_yyyymm}
            {filter_clause}
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
    return sqlite_manager.query(query, params)


def get_cost_per_by_facility_data(
    start_yyyymm: int, end_yyyymm: int, filters: Optional[dict] = None
) -> pd.DataFrame:
    filter_clause, params = build_filter_clause(filters)
    if filter_clause:
        filter_clause = f" AND {filter_clause}"
    query = f"""
        SELECT
            COALESCE(enc.FACILITY_TYPE, '(Blank)') AS FACILITY_TYPE,
            SUM(clm.PAID_AMOUNT) AS PAID_AMOUNT
        FROM FACT_CLAIMS clm
        JOIN FACT_ENCOUNTERS enc
        ON clm.ENCOUNTER_ID = enc.ENCOUNTER_ID
        WHERE clm.YEAR_MONTH BETWEEN {start_yyyymm} AND {end_yyyymm}
        {filter_clause}
        GROUP BY COALESCE(enc.FACILITY_TYPE, '(Blank)')
    """
    return sqlite_manager.query(query, params)
