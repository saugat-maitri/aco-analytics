from datetime import datetime

import plotly.express as px
from dash import Input, Output, callback

from components.bar_chart import horizontal_bar_chart
from components.no_data_figure import no_data_figure
from components.treemap_chart import treemap_chart
from reports.aco_dashboard.data import get_pmpm_performance_vs_expected_data
from reports.condition_ccsr.data import (
    get_cost_per_by_facility_data,
    get_pmpm_by_encounter_type_data,
)
from services.utils import dt_to_yyyymm, extract_sql_filters


@callback(
    Output("ccsr-encounter-group-chart", "figure"),
    Input("date-picker-input", "start_date"),
    Input("date-picker-input", "end_date"),
    Input("drillthrough-title", "children"),
)
def update_ccsr_encounter_group_chart(start_date, end_date, drillthrough_title):
    try:
        # Convert date strings to YYYYMM format for filtering
        start_yyyymm = dt_to_yyyymm(datetime.strptime(start_date, "%Y-%m-%d"))
        end_yyyymm = dt_to_yyyymm(datetime.strptime(end_date, "%Y-%m-%d"))
        filters = extract_sql_filters(ccsr_category_selection=drillthrough_title)
        data = get_pmpm_performance_vs_expected_data(
            start_yyyymm, end_yyyymm, filters=filters
        )

        return horizontal_bar_chart(
            data=data,
            x="PMPM",
            y="ENCOUNTER_GROUP",
            text_fn=["${:,.0f}".format(val) for val in data["PMPM"]],
            bar_height=45,
            show_tick_labels=False,
            plot_bgcolor="white",
            click_mode="event+select",
            custom_data=data["ENCOUNTER_GROUP"],
            text_position="outside",
            hover_template=(
                "    Encounter Group: %{customdata}   <br>"
                "    PMPM: %{text}    <br><br>"
                "<extra></extra>"
            ),
        )
    except Exception as e:
        print(f"Error in update_ccsr_encounter_group_chart: {e}")
        return no_data_figure(message=f"Error loading data: {str(e)}")


@callback(
    Output("ccsr-encounter-type-chart", "figure"),
    Input("date-picker-input", "start_date"),
    Input("date-picker-input", "end_date"),
    Input("drillthrough-title", "children"),
)
def update_ccsr_encounter_type_chart(start_date, end_date, drillthrough_title):
    try:
        # Convert date strings to YYYYMM format for filtering
        start_yyyymm = dt_to_yyyymm(datetime.strptime(start_date, "%Y-%m-%d"))
        end_yyyymm = dt_to_yyyymm(datetime.strptime(end_date, "%Y-%m-%d"))
        filters = extract_sql_filters(ccsr_category_selection=drillthrough_title)
        data = get_pmpm_by_encounter_type_data(
            start_yyyymm, end_yyyymm, filters=filters
        )

        return horizontal_bar_chart(
            data=data,
            x="PMPM",
            y="ENCOUNTER_TYPE",
            text_fn=["${:,.0f}".format(val) for val in data["PMPM"]],
            bar_height=45,
            show_tick_labels=False,
            plot_bgcolor="white",
            click_mode="event+select",
            custom_data=data["ENCOUNTER_TYPE"],
            text_position="outside",
            hover_template=(
                "    Encounter Type: %{customdata}   <br>"
                "    PMPM: %{text}    <br><br>"
                "<extra></extra>"
            ),
        )
    except Exception as e:
        print(f"Error in update_ccsr_encounter_type_chart: {e}")
        return no_data_figure(message=f"Error loading data: {str(e)}")


@callback(
    Output("ccsr-paid-by-diagnosis-chart", "figure"),
    Input("date-picker-input", "start_date"),
    Input("date-picker-input", "end_date"),
)
def update_encounter_group_treemap(start_date, end_date):
    # Your data fetching logic
    start_yyyymm = dt_to_yyyymm(datetime.strptime(start_date, "%Y-%m-%d"))
    end_yyyymm = dt_to_yyyymm(datetime.strptime(end_date, "%Y-%m-%d"))
    # filters = extract_sql_filters(ccsr_category_selection=selected_ccsr_category)
    data = get_pmpm_performance_vs_expected_data(start_yyyymm, end_yyyymm, filters=None)

    return treemap_chart(
        data=data,
        path_columns=[px.Constant("All"), "ENCOUNTER_GROUP"],
        values="PMPM",
    )


@callback(
    Output("ccsr-cost-per-by-facility-chart", "figure"),
    Input("date-picker-input", "start_date"),
    Input("date-picker-input", "end_date"),
    Input("drillthrough-title", "children"),
)
def update_cost_per_by_facility_chart(start_date, end_date, drillthrough_title):
    try:
        # Convert date strings to YYYYMM format for filtering
        start_yyyymm = dt_to_yyyymm(datetime.strptime(start_date, "%Y-%m-%d"))
        end_yyyymm = dt_to_yyyymm(datetime.strptime(end_date, "%Y-%m-%d"))
        filters = extract_sql_filters(ccsr_category_selection=drillthrough_title)
        data = get_cost_per_by_facility_data(start_yyyymm, end_yyyymm, filters=filters)

        return horizontal_bar_chart(
            data=data,
            x="PAID_AMOUNT",
            y="FACILITY_TYPE",
            text_fn=["${:,.0f}".format(val) for val in data["PAID_AMOUNT"]],
            bar_height=45,
            show_tick_labels=False,
            plot_bgcolor="white",
            click_mode="event+select",
            custom_data=data["FACILITY_TYPE"],
            text_position="outside",
            hover_template=(
                "    Facility Type: %{customdata}   <br>"
                "    Paid Amount: %{text}    <br><br>"
                "<extra></extra>"
            ),
        )
    except Exception as e:
        print(f"Error in update_cost_per_by_facility_chart: {e}")
        return no_data_figure(message=f"Error loading data: {str(e)}")
