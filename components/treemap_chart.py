import plotly.express as px

from components.no_data_figure import no_data_figure


def treemap_chart(data, path_columns, values, title=None):
    """Create a hierarchical treemap chart using plotly express.

    Args:
        data (pandas.DataFrame): Input DataFrame containing the data to plot.
        path_columns (list): List of column names representing the hierarchy path.
        values (str): Column name for the values that determine node sizes.
        title (str, optional): Chart title. Defaults to None.
        height (int, optional): Chart height in pixels. Defaults to 400.

    Returns:
        plotly.graph_objects.Figure: A plotly treemap chart figure.
    """
    if data.empty:
        return no_data_figure(message="No data available for the selected period.")

    try:
        fig = px.treemap(
            data,
            path=path_columns,
            values=values,
            color=values,
            color_continuous_scale="Blues",
            title=title,
        )

        fig.update_layout(
            margin=dict(l=20, r=20, t=40, b=20),
            plot_bgcolor="white",
            paper_bgcolor="white",
        )
        fig.data[0].hovertemplate = None

        return fig

    except Exception as e:
        print(f"Error creating treemap chart: {e}")
        return no_data_figure(message=f"Error creating chart: {str(e)}")
