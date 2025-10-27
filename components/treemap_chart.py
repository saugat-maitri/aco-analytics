import plotly.express as px

from components.no_data_figure import no_data_figure


def treemap_chart(data, path_columns, values, title=None, hovertemplate=None):
    """Create a hierarchical treemap chart using plotly express.

    Args:
        data (pandas.DataFrame): Input DataFrame containing the data to plot.
        path_columns (list): List of column names representing the hierarchy path.
        values (str): Column name for the values that determine node sizes.
        title (str, optional): Chart title. Defaults to None.
        hovertemplate (str, optional): Custom hover template for the chart. Defaults to None.

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
            color_continuous_scale=[
                "#e6f2ff",
                "#b3d9ff",
                "#80bfff",
                "#4da6ff",
                "#1a8cff",
                "#2a76ad",
            ],
            title=title,
        )

        fig.update_layout(
            margin=dict(l=10, r=10, t=20, b=15),
            plot_bgcolor="white",
            paper_bgcolor="white",
            showlegend=False,
        )
        fig.update_coloraxes(showscale=False)
        fig.data[0].hovertemplate = None

        if hovertemplate:
            fig.update_traces(hovertemplate=hovertemplate)

        return fig

    except Exception as e:
        print(f"Error creating treemap chart: {e}")
        return no_data_figure(message=f"Error creating chart: {str(e)}")
