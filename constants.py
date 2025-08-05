sqlite_path = 'cache_database.db'  # Always end with .db extension

fact_claims_query = """
SELECT 
    ENCOUNTER_ID,
    ENCOUNTER_GROUP_SK,
    ENCOUNTER_TYPE_SK,
    PRIMARY_DIAGNOSIS_CODE,
    PRIMARY_DIAGNOSIS_DESCRIPTION,
    CCSR_PARENT_CATEGORY,
    CCSR_CATEGORY,
    CCSR_CATEGORY_DESCRIPTION,
    PERSON_ID,
    YEAR_MONTH,
    SERVICE_CATEGORY_SK,
    CLAIM_ID,
    CLAIM_TYPE,
    PAID_AMOUNT
FROM FACT_CLAIMS
"""
fact_member_months_query = """
SELECT
    PERSON_ID,
    YEAR_NBR,
    YEAR_MONTH,
    MEMBER_MONTHS,
    TOTAL_YEAR_MONTHS,
    MONTHALLOCATIONFACTOR,
    DATA_SOURCE,
    PATIENT_SOURCE_KEY,
    PAYER,
    PLAN,
    NORMALIZED_RISK_SCORE,
    POPULATION_NORMALIZED_RISK_SCORE
FROM FACT_MEMBER_MONTHS
"""

dim_encounter_group_query = """
SELECT
    ENCOUNTER_GROUP,
    ENCOUNTER_GROUP_SK
FROM DIM_ENCOUNTER_GROUP
"""

dim_encounter_type_query = """
SELECT
    ENCOUNTER_TYPE,
    ENCOUNTER_TYPE_SK,
    ENCOUNTER_GROUP_SK
FROM DIM_ENCOUNTER_TYPE
"""

table_list = [
    {"table_name": "FACT_CLAIMS", "query": fact_claims_query},
    {"table_name": "FACT_MEMBER_MONTHS", "query": fact_member_months_query},
    {"table_name": "DIM_ENCOUNTER_GROUP", "query": dim_encounter_group_query},
    {"table_name": "DIM_ENCOUNTER_TYPE", "query": dim_encounter_type_query},
]
