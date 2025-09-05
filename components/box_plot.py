import plotly.express as px
from pandas import DataFrame

from components.no_data_figure import no_data_figure


def box_plot(
        data: DataFrame|None, 
        y: str ="", 
        points: str|bool =False,
        xaxis_title: str ="", 
        yaxis_title: str ="", 
        show_legend: bool =False, 
        show_line: bool =False, 
        height=None
    ):
    """Create a box plot visualization using plotly express.

    Args:
        data : Input DataFrame containing the data to plot. If None or empty, returns no data figure.
        y : Column name from DataFrame to plot on y-axis. Default ""
        points : Display style for points. Options include 'outliers', 'all', or 'False'. Default ""
        xaxis_title : Title for x-axis label. Default ""
        yaxis_title : Title for y-axis label. Default ""
        show_legend : Whether to display the plot legend. Default False
        show_line : Whether to show axis lines. Default False
        height : Custom height for the plot in pixels. If None, defaults to 117.

    Returns:
        plotly.graph_objects.Figure: A plotly Figure object containing the box plot visualization or no data figure if input is empty.

    Notes:
        - The plot is styled with a white background and minimal grid lines for a clean look.
        - Only outlier points are shown in the box plot.
    """
    box_height = height or 117

    if data is not None and data.empty:
        return no_data_figure(message="No data available for the selected period.")

    fig = px.box(data, y=y, points=points)

    fig.update_layout(
        plot_bgcolor='white',
        showlegend=show_legend,
        yaxis_title=yaxis_title,
        xaxis_title=xaxis_title,
        margin=dict(l=10, r=10, t=10, b=10),
        height=box_height,
    )
    # Clean up grid and axis lines for a cleaner look
    fig.update_xaxes(showgrid=False, visible=False)
    fig.update_yaxes(showgrid=True, zeroline=False, ticks="outside", showline=show_line, linewidth=1, linecolor="#ccc")
    return fig
