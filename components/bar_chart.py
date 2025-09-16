import pandas as pd
import plotly.express as px
import plotly.graph_objs as go

from components.no_data_figure import no_data_figure


def vertical_bar_chart(
    data,
    x,
    y,
    color_fn=None,
    text_fn=None,
    margin=None,
    marker_color=None,
    showticklabels=True,
    plot_bgcolor="white",
    clickmode="event+select",
    customdata=None,
    textposition=None,
    hovertemplate=None,
    hoverbackgroundcolor='white',
    hovertextcolor='black',
):
    """Create and return a vertical bar chart using plotly.

    Args:
        data (pandas.DataFrame): Input DataFrame containing the data to plot.
        x (array-like): Values for x-axis.
        y (array-like): Values for y-axis. Can be a pandas Series or list.
        color_fn (callable, optional): Function to determine bar colors based on y values. Defaults to None.
        text_fn (callable, optional): Function to determine bar text labels based on y values. Defaults to None.
        margin (dict, optional): Chart margins in format {l, r, t, b}. Defaults to {l:20, r:20, t:20, b:20}.
        marker_color (str/list, optional): Color(s) for bars. Used if color_fn is None. Defaults to None.
        showticklabels (bool, optional): Whether to show tick labels on y-axis. Defaults to True.
        plot_bgcolor (str, optional): Background color of the plot. Defaults to 'white'.
        clickmode (str, optional): Chart click interaction mode. Defaults to 'event+select'.
        customdata (array-like, optional): Custom data for hover template. Defaults to None.
        textposition (str, optional): Position of bar text labels ('inside' or 'outside'). Defaults to 'outside'.
        hovertemplate (str, optional): Template for hover text. Defaults to None.
        hoverbackgroundcolor (str, optional): Background color for hover labels. Defaults to 'white'.
        hovertextcolor (str, optional): Text color for hover labels. Defaults to 'black'.

    Returns:
        plotly.graph_objects.Figure: A plotly vertical bar chart figure.

    Notes:
        - Chart height is dynamically calculated based on number of bars
        - Minimum height is 200px
        - Bar height is fixed at 40px
        - Y-axis range is automatically set to 110% of maximum y value
        - Handles empty data gracefully.
    """
    if data.empty:
        return no_data_figure(message="No data available for the selected period.")

    x_value = data[x]
    y_value = data[y]
    custom = (
        customdata if customdata is not None else y if hasattr(y, "empty") else None
    )

    max_value = max(y_value) if not y_value.empty else 0
    n_bars = len(x_value) if not x_value.empty else 1
    y_range_max = max_value * 1.2 if max_value > 0 else 1
    bar_height = 40
    min_height = 200
    fig_height = max(
        min_height, n_bars * bar_height + 100
    )  # Define the height of the bar to maintain the proper height of graph

    fig = go.Figure(
        go.Bar(
            x=x_value,
            y=y_value,
            orientation="v",
            marker_color=color_fn if color_fn else marker_color,
            text=text_fn,
            textposition=textposition,
            hovertemplate=hovertemplate,
            hoverlabel=dict(
                bgcolor=hoverbackgroundcolor,
                font=dict(color=hovertextcolor)
            ),
            customdata=custom,
        )
    )
    fig.update_layout(
        margin=margin or dict(l=20, r=20, t=20, b=20),
        xaxis=dict(automargin=True),
        yaxis=dict(showticklabels=showticklabels, range=[0, y_range_max]),
        plot_bgcolor=plot_bgcolor,
        clickmode=clickmode,
        height=fig_height,
    )
    return fig


def horizontal_bar_chart(
    data,
    x,
    y,
    color_fn=None,
    text_fn=None,
    margin=None,
    marker_color=None,
    showticklabels=True,
    plot_bgcolor="white",
    clickmode="event+select",
    customdata=None,
    textposition=None,
    hovertemplate=None,
    hoverbackgroundcolor='white',
    hovertextcolor='black',
):
    """Create and return a horizontal bar chart using plotly.

    Args:
        data (pandas.DataFrame): Input DataFrame containing the data to plot.
        x (array-like): Values for the horizontal bars (bar lengths). Can be a pandas Series or list.
        y (array-like): Labels for the bars (y-axis).
        color_fn (callable, optional): Function to determine bar colors based on x values. Defaults to None.
        text_fn (callable, optional): Function to determine text display for each bar based on x values. Defaults to None.
        margin (dict, optional): Chart margins in format {l, r, t, b}. Defaults to {l:20, r:20, t:20, b:20}.
        marker_color (str, optional): Color(s) for bars. Used if color_fn is None. Defaults to None.
        showticklabels (bool, optional): Whether to show x-axis tick labels. Defaults to True.
        plot_bgcolor (str, optional): Background color of the plot. Defaults to 'white'.
        clickmode (str, optional): Mode for handling click events. Defaults to 'event+select'.
        customdata (array-like, optional): Custom data for hover information. Defaults to None.
        textposition (str, optional): Position of text labels ('inside' or 'outside'). Defaults to 'outside'.
        hovertemplate (str, optional): Template for hover information display. Defaults to None.
        hoverbackgroundcolor (str, optional): Background color for hover labels. Defaults to 'white'.
        hovertextcolor (str, optional): Text color for hover labels. Defaults to 'black'.

    Returns:
        plotly.graph_objs.Figure: A horizontal bar chart figure object.

    Notes:
        - The chart height adjusts automatically based on the number of bars
        - Bars are displayed in reversed order (top to bottom)
        - The x-axis range extends 10% beyond the maximum value
    """
    if data.empty:
        return no_data_figure(message="No data available for the selected period.")

    x_value = data[x]
    y_value = data[y]
    custom = (
        customdata if customdata is not None else y_value
    )  # Use custom data if provided, else use y values fot the text

    max_value = max(x_value) if not x_value.empty else 0
    n_bars = len(y_value) if not y_value.empty else 1
    x_range_max = max_value * 1.2 if max_value > 0 else 1
    bar_height = 20
    min_height = 200
    fig_height = max(
        min_height, n_bars * bar_height + 100
    )  # Define the height of the bar to maintain the proper height of graph

    fig = go.Figure(
        go.Bar(
            x=x_value,
            y=y_value,
            orientation="h",
            marker_color=color_fn if color_fn else marker_color,
            text=text_fn,
            textposition=textposition,
            hovertemplate=hovertemplate,
            hoverlabel=dict(
                bgcolor=hoverbackgroundcolor,
                font=dict(color=hovertextcolor)
            ),
            customdata=custom,
        )
    )
    fig.update_layout(
        margin=margin or dict(l=20, r=20, t=0, b=0),
        yaxis=dict(autorange="reversed"),
        xaxis=dict(showticklabels=showticklabels, range=[0, x_range_max]),
        plot_bgcolor=plot_bgcolor,
        clickmode=clickmode,
        height=fig_height,
    )
    return fig


def stacked_percentage_bar(
    data: pd.DataFrame,
    x: str,
    group_col: str,
    height: int = 120,
):
    """Create and return a stacked percentage bar chart using plotly.

    Args:
        data (pandas.DataFrame): Input DataFrame containing the data to plot.
        x (str): Column name containing numeric values to be represented as percentages.
        group_col (str): Column name containing group labels for each bar segment.
        height (int, optional): Height of the chart in pixels. Defaults to 120.

    Returns:
        plotly.graph_objects.Figure: A plotly stacked percentage bar chart figure.
    """
    color_scheme = px.colors.qualitative.Set2

    total = data[x].sum()
    data["PCT"] = (data[x] / total * 100).round(1) if total > 0 else 0

    fig = go.Figure()

    for i, row in data.iterrows():
        fig.add_bar(
            x=[row["PCT"]],
            y=[""],
            orientation="h",
            name=row[group_col],
            text=[f"{row['PCT']:.0f}%"],
            textposition="inside",
            insidetextanchor="middle",
            customdata=[[x, row[group_col]]],
            hovertemplate=(
                "<b>%{customdata[1]}</b><br>%{customdata[0]}: %{x:,.2f}%<extra></extra>"
            ),
            marker_color=color_scheme[i % len(color_scheme)],
        )

    fig.update_layout(
        barmode="stack",
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(automargin=True, showgrid=False, zeroline=False, ticksuffix="%"),
        yaxis=dict(showticklabels=False),
        plot_bgcolor="white",
        height=height,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.1,
            xanchor="center",
            x=0.5,
        ),
    )

    return fig
