from dash import Input, Output, callback
import pandas as pd

from components import kpi_card


@callback(
    Output("comparison-pmpm", "children"),
    Output("comparison-utilization", "children"),
    Output("comparison-cost", "children"),
    Input("year-dropdown", "value")
)
def update_comparison_text(comparison_period):
    return comparison_period, comparison_period, comparison_period

@callback(
    Output("pmpm-cost-card", "children"),
    Output("utilization-card", "children"),
    Output("cost-per-encounter-card", "children"),
    Input("my-date-picker-range", "start_date"),
    Input("my-date-picker-range", "end_date"),
    Input("year-dropdown", "value")
)
def update_kpi_cards(start_date, end_date, comparison_period):
    claims_agg = pd.read_csv("data/outlier_claims_agg.csv")
    member_months = pd.read_csv("data/outlier_member_months.csv")

    claims_agg_df = claims_agg[(claims_agg["INCR_YEAR"] >= int(start_date[:4])) & (claims_agg["INCR_YEAR"] <= int(end_date[:4]))]
    member_months_df = member_months[(member_months["YEAR"] >= int(start_date[:4])) & (member_months["YEAR"] <= int(end_date[:4]))]

    pmpm_cost = "${:,.0f}".format(claims_agg_df["PAID_AMOUNT"].sum() / member_months_df[["MEMBER_ID", "YEAR_MONTH"]].drop_duplicates().shape[0])
    utilization = "{:,.0f}".format((claims_agg_df["ENCOUNTER_ID"].nunique() / member_months_df[["MEMBER_ID", "YEAR_MONTH"]].drop_duplicates().shape[0]) * 12000)
    cost_per_encounter = "${:,.0f}".format(claims_agg_df["PAID_AMOUNT"].sum() / claims_agg_df["ENCOUNTER_ID"].nunique())
    # Comparison values (dummy for now)
    last_year = 200
    expected = 300
    compare_text = "+0.0%"
    expected_text = "+0.0%"
    # Return dynamic cards
    return (
        kpi_card("PMPM Cost", pmpm_cost, compare_text, expected_text, last_year, expected, "comparison-pmpm"),
        kpi_card("Utilization (PKPY)", utilization, compare_text, expected_text, last_year, expected, "comparison-utilization"),
        kpi_card("Cost Per Encounter", cost_per_encounter, compare_text, expected_text, last_year, expected, "comparison-cost")
    )