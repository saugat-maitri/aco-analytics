from datetime import datetime

import pandas as pd
from dash import Input, Output, callback

from components.bar_chart import horizontal_bar_chart, stacked_percentage_bar
from components.demographics_card import demographics_card
from components.kpi_card import kpi_card
from components.no_data_figure import no_data_figure
from components.trend_chart import trend_chart
from services.utils import (
    dt_to_yyyymm,
    extract_sql_filters,
    get_comparison_offset,
    get_comparison_period,
    truncate_text,
)

from .data import (
    calc_kpis,
    get_condition_ccsr_data,
    get_demographic_data,
    get_encounter_type_pmpm_data,
    get_pmpm_performance_vs_expected_data,
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
def update_kpi_cards(start_date, end_date, comparison_period, group_click, ccsr_click):
    start_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")

    start_comp, end_comp = get_comparison_period(
        start_date, end_date, comparison_period
    )

    filters = extract_sql_filters(group_click, ccsr_click)
    pmpm_main = calc_kpis(start_date, end_date, filters)
    pmpm_comp = calc_kpis(start_comp, end_comp, filters)

    # Comparison values (dummy for now)
    expected = 300
    # Return dynamic cards
    return (kpi_card("PMPM Cost", pmpm_main, pmpm_comp, expected, "comparison-pmpm"),)


@callback(
    Output("pmpm-trend", "figure"),
    Input("date-picker-input", "start_date"),
    Input("date-picker-input", "end_date"),
    Input("comparison-period-dropdown", "value"),
    Input("encounter-group-chart", "selectedData"),
    Input("condition-ccsr-chart", "selectedData"),
)
def update_pmpm_trend(start_date, end_date, comparison_period, group_click, ccsr_click):
    filters = extract_sql_filters(group_click, ccsr_click)

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

        return horizontal_bar_chart(
            data=data,
            x="PMPM",
            y="ENCOUNTER_GROUP",
            color_fn=["#ed3030" if val > 400 else "#428c8d" for val in data["PMPM"]],
            text_fn=["${:,.0f}".format(val) for val in data["PMPM"]],
            margin=dict(l=20, r=20, t=20, b=20),
            marker_color="#64AFE0",
            showticklabels=False,
            plot_bgcolor="white",
            clickmode="event+select",
            customdata=data["ENCOUNTER_GROUP"],
            textposition="outside",
            hovertemplate=(
                "Encounter Group: %{customdata}<br>PMPM: %{text}<extra></extra>"
            ),
        )

    except Exception as e:
        print(f"Error in update_pmpm_performance_vs_expected: {e}")
        return no_data_figure(message=f"Error loading data: {str(e)}")


@callback(
    Output("encounter-group-percentage-chart", "figure"),
    Input("date-picker-input", "start_date"),
    Input("date-picker-input", "end_date"),
)
def update_encounter_group_percentage_chart(start_date, end_date):
    try:
        # Convert date strings to YYYYMM format for filtering
        start_yyyymm = dt_to_yyyymm(datetime.strptime(start_date, "%Y-%m-%d"))
        end_yyyymm = dt_to_yyyymm(datetime.strptime(end_date, "%Y-%m-%d"))

        data = get_pmpm_performance_vs_expected_data(start_yyyymm, end_yyyymm)

        return stacked_percentage_bar(
            data=data,
            x="PMPM",
            group_col="ENCOUNTER_GROUP",
            height=120,
        )

    except Exception as e:
        print(f"Error in update_encounter_group_percentage_chart: {e}")
        return no_data_figure(message=f"Error loading data: {str(e)}")


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

        return horizontal_bar_chart(
            data=data,
            x="PMPM",
            y="ENCOUNTER_TYPE",
            color_fn=["#ed3030" if val > 400 else "#428c8d" for val in data["PMPM"]],
            text_fn=[f"${v:,.0f}" for v in data["PMPM"]],
            margin=dict(l=20, r=20, t=20, b=20),
            showticklabels=False,
            customdata=data["ENCOUNTER_TYPE"],
            hovertemplate=(
                "Encounter Type: %{customdata}<br>PMPM: %{text}<br><extra></extra>"
            ),
        )

    except Exception as e:
        print(f"Error in update_encounter_type_pmpm_bar: {e}")
        return f"Error loading data: {str(e)}"
