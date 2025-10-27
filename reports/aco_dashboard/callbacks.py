from datetime import datetime

import pandas as pd
from dash import Input, Output, State, callback, html, no_update

from components.bar_chart import horizontal_bar_chart, stacked_percentage_bar
from components.demographics_card import demographics_card
from components.kpi_card import kpi_card
from components.no_data_figure import no_data_figure
from components.trend_chart import trend_chart
from services.utils import (
    dt_to_yyyymm,
    extract_sql_filters,
    format_large_number,
    get_comparison_offset,
    get_comparison_period,
    truncate_text,
)

from .data import (
    calc_kpis,
    get_cohort_data,
    get_condition_ccsr_data,
    get_demographic_data,
    get_encounter_group_expected_pmpm,
    get_encounter_group_pmpm,
    get_trends_data,
)


@callback(
    Output("comparison-pmpm", "children"), Input("comparison-period-dropdown", "value")
)
def update_comparison_text(comparison_period):
    return comparison_period


@callback(
    Output("pmpm-cost-card", "children"),
    Input("date-picker-input", "start_date"),
    Input("date-picker-input", "end_date"),
    Input("comparison-period-dropdown", "value"),
    Input("encounter-group-chart", "selectedData"),
    Input("condition-ccsr-chart", "selectedData"),
)
def update_kpi_cards(
    start_date, end_date, comparison_period, selected_group, selected_ccsr_category
):
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    start_comp, end_comp = get_comparison_period(
        start_date, end_date, comparison_period
    )

    filters = extract_sql_filters(
        group_selection=selected_group, ccsr_category_selection=selected_ccsr_category
    )
    pmpm_main, pmpm_expected = calc_kpis(start_date, end_date, filters)
    pmpm_comp, pmpm_expected_comp = calc_kpis(start_comp, end_comp, filters)

    # Return dynamic cards
    return (
        kpi_card("PMPM Cost", pmpm_main, pmpm_comp, pmpm_expected, "comparison-pmpm"),
    )


@callback(
    Output("pmpm-trend", "figure"),
    Input("date-picker-input", "start_date"),
    Input("date-picker-input", "end_date"),
    Input("comparison-period-dropdown", "value"),
    Input("encounter-group-chart", "selectedData"),
    Input("condition-ccsr-chart", "selectedData"),
)
def update_pmpm_trend(
    start_date, end_date, comparison_period, selected_group, selected_ccsr_category
):
    filters = extract_sql_filters(
        group_selection=selected_group, ccsr_category_selection=selected_ccsr_category
    )

    df = get_trends_data(filters)

    start = pd.to_datetime(start_date).replace(day=1)
    end = pd.to_datetime(end_date).replace(day=1)
    selected_months = pd.date_range(start=start, end=end, freq="MS")

    current_data = []
    if not df.empty:
        df["YEAR_MONTH"] = pd.to_datetime(df["YEAR_MONTH"].astype(str), format="%Y%m")
        current_df = df[df["YEAR_MONTH"].isin(selected_months)]
        current_data = list(zip(current_df["YEAR_MONTH"], current_df["PMPM"]))

    comparison_data = []
    for month in selected_months:
        comp_range = get_comparison_offset(month, comparison_period, selected_months)
        comp_df = df[df["YEAR_MONTH"].isin(comp_range)]
        total_paid = comp_df["TOTAL_PAID"].sum()
        total_members = comp_df["MEMBERS_COUNT"].sum()

        avg_pmpm = total_paid / total_members if total_members > 0 else 0
        comparison_data.append((month, avg_pmpm))
    return trend_chart(current_data, comparison_data)


@callback(
    Output("condition-ccsr-chart", "figure"),
    Input("date-picker-input", "start_date"),
    Input("date-picker-input", "end_date"),
    Input("encounter-group-chart", "selectedData"),
)
def update_condition_ccsr_cost_driver_graph(start_date, end_date, selected_group):
    try:
        # Convert date strings to YYYYMM format for filtering
        start_yyyymm = dt_to_yyyymm(datetime.strptime(start_date, "%Y-%m-%d"))
        end_yyyymm = dt_to_yyyymm(datetime.strptime(end_date, "%Y-%m-%d"))
        filters = extract_sql_filters(group_selection=selected_group)
        ccsr_data = get_condition_ccsr_data(start_yyyymm, end_yyyymm, filters)

        return horizontal_bar_chart(
            data=ccsr_data,
            x="PMPM",
            y="CCSR_CATEGORY_DESCRIPTION",
            text_fn=[f"${v:,.0f}" for v in ccsr_data["PMPM"]],
            show_tick_labels=False,
            custom_data=ccsr_data["CCSR_CATEGORY_DESCRIPTION"],
            hover_template=(
                "CCSR Category: %{customdata}<br>PMPM: %{text}<br><extra></extra>"
            ),
            truncate_limit=40,
        )
    except Exception as e:
        print(f"Error in update_condition_ccsr_cost_driver_graph: {e}")
        return f"Error loading data: {str(e)}"


@callback(
    Output("members-card", "children"),
    Output("percentage-female-card", "children"),
    Output("risk-score-card", "children"),
    Input("date-picker-input", "start_date"),
    Input("date-picker-input", "end_date"),
    Input("comparison-period-dropdown", "value"),
)
def update_demographic_data(start_date, end_date, comparison_period):
    try:
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

        comp_start_date, comp_end_date = get_comparison_period(
            start_date, end_date, comparison_period
        )

        demographic_data = get_demographic_data(start_date, end_date)
        comp_demographic_data = get_demographic_data(comp_start_date, comp_end_date)

        return [
            demographics_card(
                "Members",
                demographic_data.get("TOTAL_MEMBER_MONTHS", 0).iloc[0],
                comp_demographic_data.get("TOTAL_MEMBER_MONTHS", 0).iloc[0],
                comparison_period,
            ),
            demographics_card(
                "Female %",
                round(demographic_data.get("PERCENT_FEMALE", 0).iloc[0]),
                round(comp_demographic_data.get("PERCENT_FEMALE", 0).iloc[0]),
                comparison_period,
                value_suffix="%",
            ),
            demographics_card(
                "Risk Score",
                round(demographic_data.get("AVG_RISK_SCORE", 0).iloc[0], 2),
                round(comp_demographic_data.get("AVG_RISK_SCORE", 0).iloc[0], 2),
                comparison_period,
            ),
        ]

    except Exception as e:
        print(f"Error in update_demographic_data: {e}")
        return no_data_figure(message=f"Error loading data: {str(e)}")


@callback(
    Output("encounter-group-chart", "figure"),
    Input("date-picker-input", "start_date"),
    Input("date-picker-input", "end_date"),
    Input("condition-ccsr-chart", "selectedData"),
)
def update_pmpm_performance_vs_expected(start_date, end_date, selected_ccsr_category):
    try:
        # Convert date strings to YYYYMM format for filtering
        start_yyyymm = dt_to_yyyymm(datetime.strptime(start_date, "%Y-%m-%d"))
        end_yyyymm = dt_to_yyyymm(datetime.strptime(end_date, "%Y-%m-%d"))
        filters = extract_sql_filters(ccsr_category_selection=selected_ccsr_category)

        data = get_encounter_group_pmpm(start_yyyymm, end_yyyymm, filters)
        expected_pmpm = get_encounter_group_expected_pmpm(
            start_yyyymm, end_yyyymm
        ).melt(var_name="ENCOUNTER_GROUP", value_name="EXPECTED_PMPM")

        # Merge actual and expected data
        merged_data = pd.merge(data, expected_pmpm, on="ENCOUNTER_GROUP", how="left")

        # Determine if expected PMPM data is available
        show_expected = not merged_data["EXPECTED_PMPM"].isna().all()

        # Configure hover data based on expected PMPM availability
        if show_expected:
            custom_data = merged_data[["ENCOUNTER_GROUP", "PMPM", "EXPECTED_PMPM"]]
            hover_template = (
                "Encounter Group: %{customdata[0]}<br>"
                "Actual PMPM: %{customdata[1]:,.2f}<br>"
                "Expected PMPM: %{customdata[2]:,.2f}<br>"
                "<extra></extra>"
            )
        else:
            custom_data = merged_data[["ENCOUNTER_GROUP", "PMPM"]]
            hover_template = (
                "Encounter Group: %{customdata[0]}<br>"
                "Actual PMPM: %{customdata[1]:,.2f}<br>"
                "<extra></extra>"
            )
        return horizontal_bar_chart(
            data=merged_data,
            x="PMPM",
            y="ENCOUNTER_GROUP",
            target="EXPECTED_PMPM" if show_expected else None,
            text_fn=["${:,.0f}".format(val) for val in merged_data["PMPM"]],
            bar_height=45,
            show_tick_labels=False,
            plot_bgcolor="white",
            click_mode="event+select",
            custom_data=custom_data,
            text_position="outside",
            hover_template=hover_template,
        )
    except Exception as e:
        print(f"Error in update_pmpm_performance_vs_expected: {e}")
        return no_data_figure(message=f"Error loading data: {str(e)}")


@callback(
    Output("encounter-group-percentage-chart", "figure"),
    Input("date-picker-input", "start_date"),
    Input("date-picker-input", "end_date"),
    Input("condition-ccsr-chart", "selectedData"),
)
def update_encounter_group_percentage_chart(
    start_date, end_date, selected_ccsr_category
):
    try:
        # Convert date strings to YYYYMM format for filtering
        start_yyyymm = dt_to_yyyymm(datetime.strptime(start_date, "%Y-%m-%d"))
        end_yyyymm = dt_to_yyyymm(datetime.strptime(end_date, "%Y-%m-%d"))
        filters = extract_sql_filters(ccsr_category_selection=selected_ccsr_category)

        data = get_encounter_group_pmpm(start_yyyymm, end_yyyymm, filters)

        return stacked_percentage_bar(
            data=data,
            x="PMPM",
            group_col="ENCOUNTER_GROUP",
            height=90,
        )
    except Exception as e:
        print(f"Error in update_encounter_group_percentage_chart: {e}")
        return no_data_figure(message=f"Error loading data: {str(e)}")


@callback(
    Output("paid-by-cohort-chart", "figure"),
    Input("date-picker-input", "start_date"),
    Input("date-picker-input", "end_date"),
    Input("encounter-group-chart", "selectedData"),
    Input("condition-ccsr-chart", "selectedData"),
)
def update_cohort_data(start_date, end_date, selected_group, selected_ccsr_category):
    try:
        # Convert date strings to YYYYMM format for filtering
        start_yyyymm = dt_to_yyyymm(datetime.strptime(start_date, "%Y-%m-%d"))
        end_yyyymm = dt_to_yyyymm(datetime.strptime(end_date, "%Y-%m-%d"))
        filters = extract_sql_filters(
            group_selection=selected_group,
            ccsr_category_selection=selected_ccsr_category,
        )

        data = get_cohort_data(start_yyyymm, end_yyyymm, filters)

        return horizontal_bar_chart(
            data=data,
            x="total_paid_amount",
            y="percent_group",
            text_fn=[
                f"${format_large_number(v)} {pct:.1f}%"
                for v, pct in zip(data["total_paid_amount"], data["percent_of_total"])
            ],
            bar_height=45,
            click_mode="event",
            show_tick_labels=True,
            text_position=None,
            hover_template=(
                "   Group: %{y}   <br>"
                "   Total Paid by Percentile Group: $%{x:,.2f}   <br>"
                "<extra></extra>"
            ),
        )
    except Exception as e:
        print(f"Error in update_cohort_data: {e}")
        return no_data_figure(message=f"Error loading data: {str(e)}")


@callback(
    Output("floating-drillthrough-btn-container", "children"),
    Input("drillthrough-selection", "data"),
)
def show_floating_button(selection):
    if not selection:
        return None

    label = selection["label"]

    button_text = f"Drill Through → {label}"
    button = html.Button(
        button_text,
        id="floating-drillthrough-btn",
        n_clicks=0,
        style={
            "backgroundColor": "#007bff",
            "color": "white",
            "border": "none",
            "padding": "10px 20px",
            "borderRadius": "8px",
            "boxShadow": "0 2px 8px rgba(0,0,0,0.2)",
            "cursor": "pointer",
            "fontSize": "12px",
            "fontWeight": "600",
        },
    )

    return button


@callback(
    Output("drillthrough-selection", "data", allow_duplicate=True),
    Input("condition-ccsr-chart", "selectedData"),
    prevent_initial_call=True,
)
def select_condition_ccsr(selectedData):
    if not selectedData or "points" not in selectedData:
        return None

    ccsr_name = selectedData["points"][0].get("customdata") or selectedData["points"][
        0
    ].get("y")
    return {"chart": "condition-ccsr", "label": ccsr_name}


@callback(
    Output("drillthrough-selection", "data", allow_duplicate=True),
    Input("encounter-group-chart", "selectedData"),
    prevent_initial_call=True,
)
def select_encounter_group(selectedData):
    if not selectedData or "points" not in selectedData:
        return None

    group_name = selectedData["points"][0].get("customdata") or selectedData["points"][
        0
    ].get("y")
    return {"chart": "encounter-group", "label": group_name}


@callback(
    Output("url", "href"),
    Input("floating-drillthrough-btn", "n_clicks"),
    State("drillthrough-selection", "data"),
    prevent_initial_call=True,
)
def handle_redirect(n_clicks, selection):
    if not n_clicks or not selection:
        return no_update

    chart = selection["chart"]
    label = selection["label"]

    if chart == "condition-ccsr":
        return f"/condition-ccsr?ccsr={label}"
    elif chart == "encounter-group":
        return f"/encounter-group?group={label}"
    else:
        return no_update
