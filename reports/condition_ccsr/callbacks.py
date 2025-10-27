from datetime import datetime

import plotly.express as px
from dash import Input, Output, callback, ctx
from dash.exceptions import PreventUpdate

from components.bar_chart import horizontal_bar_chart
from components.metric_card import metric_card
from components.no_data_figure import no_data_figure
from components.treemap_chart import treemap_chart
from reports.aco_dashboard.data import get_pmpm_performance_vs_expected_data
from reports.condition_ccsr.data import (
    get_ccsr_metrics_data,
    get_cost_per_by_facility_data,
    get_paid_by_diagnosis_data,
    get_pmpm_by_encounter_type_data,
)
from services.utils import dt_to_yyyymm, extract_sql_filters, format_large_number


@callback(
    Output("ccsr-active-filters-store", "data"),
    Input("drillthrough-title", "children"),
    Input("ccsr-encounter-group-chart", "selectedData"),
    Input("ccsr-encounter-type-chart", "selectedData"),
    Input("ccsr-paid-by-diagnosis-chart", "clickData"),
)
def update_active_filter(
    drillthrough_title, selected_group, selected_type, selected_diagnosis
):
    filters = {}
    if drillthrough_title:
        filters["CCSR_CATEGORY_DESCRIPTION"] = drillthrough_title

    if (
        ctx.triggered_id == "ccsr-encounter-group-chart"
        and selected_group
        and selected_group.get("points")
    ):
        group_filters = extract_sql_filters(group_selection=selected_group)
        filters.update(group_filters)

    elif (
        ctx.triggered_id == "ccsr-encounter-type-chart"
        and selected_type
        and selected_type.get("points")
    ):
        type_filters = extract_sql_filters(encounter_type_selection=selected_type)
        filters.update(type_filters)

    elif (
        ctx.triggered_id == "ccsr-paid-by-diagnosis-chart"
        and selected_diagnosis
        and selected_diagnosis.get("points")
    ):
        points = selected_diagnosis.get("points")
        if (
            points[0].get("entry")
            and points[0]["entry"] == "All"
            and not points[0].get("label") == "All"
        ):
            diagnosis_filters = extract_sql_filters(
                diagnosis_selection=selected_diagnosis
            )
            filters.update(diagnosis_filters)

    return filters


@callback(
    Output("ccsr-metrics-container", "children"),
    Input("date-picker-input", "start_date"),
    Input("date-picker-input", "end_date"),
    Input("ccsr-active-filters-store", "data"),
)
def update_ccsr_metrics(start_date, end_date, active_filters):
    try:
        # Convert date strings to YYYYMM format for filtering
        start_yyyymm = dt_to_yyyymm(datetime.strptime(start_date, "%Y-%m-%d"))
        end_yyyymm = dt_to_yyyymm(datetime.strptime(end_date, "%Y-%m-%d"))

        data = get_ccsr_metrics_data(start_yyyymm, end_yyyymm, filters=active_filters)

        if data.empty:
            return no_data_figure(message="No data available for the selected period.")

        pmpm = data["PMPM"].iloc[0]
        cost_per_encounter = format_large_number(data["COST_PER_ENCOUNTER"].iloc[0])
        pkpy = format_large_number(data["PKPY"].iloc[0])
        members = format_large_number(data["total_members"].iloc[0])
        return [
            metric_card(
                title="PMPM Cost",
                value=f"${pmpm:,.0f}",
            ),
            metric_card(
                title="Cost Per Encounter",
                value=f"${cost_per_encounter}",
            ),
            metric_card(
                title="PKPY",
                value=f"{pkpy}",
            ),
            metric_card(
                title="Members",
                value=f"{members}",
            ),
        ]
    except Exception as e:
        print(f"Error in update_ccsr_metrics: {e}")
        return no_data_figure(message=f"Error loading data: {str(e)}")


@callback(
    Output("ccsr-encounter-group-chart", "figure"),
    Input("date-picker-input", "start_date"),
    Input("date-picker-input", "end_date"),
    Input("ccsr-active-filters-store", "data"),
    Input("ccsr-encounter-group-chart", "selectedData"),
)
def update_ccsr_encounter_group_chart(
    start_date, end_date, active_filters, selected_group
):
    if ctx.triggered_id == "ccsr-encounter-group-chart" and selected_group:
        raise PreventUpdate

    try:
        # Convert date strings to YYYYMM format for filtering
        start_yyyymm = dt_to_yyyymm(datetime.strptime(start_date, "%Y-%m-%d"))
        end_yyyymm = dt_to_yyyymm(datetime.strptime(end_date, "%Y-%m-%d"))

        data = get_pmpm_performance_vs_expected_data(
            start_yyyymm, end_yyyymm, filters=active_filters
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
    Input("ccsr-active-filters-store", "data"),
    Input("ccsr-encounter-type-chart", "selectedData"),
)
def update_ccsr_encounter_type_chart(
    start_date, end_date, active_filters, selected_type
):
    if ctx.triggered_id == "ccsr-encounter-type-chart" and selected_type:
        raise PreventUpdate

    try:
        # Convert date strings to YYYYMM format for filtering
        start_yyyymm = dt_to_yyyymm(datetime.strptime(start_date, "%Y-%m-%d"))
        end_yyyymm = dt_to_yyyymm(datetime.strptime(end_date, "%Y-%m-%d"))

        data = get_pmpm_by_encounter_type_data(
            start_yyyymm, end_yyyymm, filters=active_filters
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
            truncate_limit=20,
        )
    except Exception as e:
        print(f"Error in update_ccsr_encounter_type_chart: {e}")
        return no_data_figure(message=f"Error loading data: {str(e)}")


@callback(
    Output("ccsr-paid-by-diagnosis-chart", "figure"),
    Input("date-picker-input", "start_date"),
    Input("date-picker-input", "end_date"),
    Input("ccsr-active-filters-store", "data"),
    Input("ccsr-paid-by-diagnosis-chart", "clickData"),
)
def update_paid_by_diagnosis_treemap(
    start_date, end_date, active_filters, selected_diagnosis
):
    if ctx.triggered_id == "ccsr-paid-by-diagnosis-chart" and selected_diagnosis:
        raise PreventUpdate

    start_yyyymm = dt_to_yyyymm(datetime.strptime(start_date, "%Y-%m-%d"))
    end_yyyymm = dt_to_yyyymm(datetime.strptime(end_date, "%Y-%m-%d"))
    data = get_paid_by_diagnosis_data(start_yyyymm, end_yyyymm, filters=active_filters)

    return treemap_chart(
        data=data,
        path_columns=[px.Constant("All"), "PRIMARY_DIAGNOSIS_DESCRIPTION"],
        values="PAID_AMOUNT",
        hovertemplate="<b>%{label}</b><br>Paid Amount: $%{value:,.0f}<extra></extra>",
    )


@callback(
    Output("ccsr-cost-per-by-facility-chart", "figure"),
    Input("date-picker-input", "start_date"),
    Input("date-picker-input", "end_date"),
)
def update_cost_per_by_facility_chart(start_date, end_date):
    try:
        # Convert date strings to YYYYMM format for filtering
        start_yyyymm = dt_to_yyyymm(datetime.strptime(start_date, "%Y-%m-%d"))
        end_yyyymm = dt_to_yyyymm(datetime.strptime(end_date, "%Y-%m-%d"))
        data = get_cost_per_by_facility_data(start_yyyymm, end_yyyymm, filters=None)

        return horizontal_bar_chart(
            data=data,
            x="PAID_AMOUNT",
            y="FACILITY_TYPE",
            text_fn=[f"${format_large_number(val)}" for val in data["PAID_AMOUNT"]],
            bar_height=45,
            show_tick_labels=False,
            plot_bgcolor="white",
            click_mode="event+select",
            custom_data=data[["FACILITY_TYPE", "PAID_AMOUNT"]],
            text_position="outside",
            hover_template=(
                "    Facility Type: %{customdata[0]}   <br>"
                "    Paid Amount: $%{customdata[1]:,.2f}    <br><br>"
                "<extra></extra>"
            ),
            truncate_limit=20,
        )
    except Exception as e:
        print(f"Error in update_cost_per_by_facility_chart: {e}")
        return no_data_figure(message=f"Error loading data: {str(e)}")
