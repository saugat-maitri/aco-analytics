import plotly.graph_objs as go


def no_data_figure(message="No data available for the selected period"):
    """Generate a plotly figure displaying error message.

    This function creates an empty figure with a centered text annotation, typically used
    as a placeholder when data visualization is not possible due to lack of data.

    Args:
        message (str, optional): The message to display in the center of the figure.
            Defaults to "No data available for the selected period".

    Returns:
        go.Figure: A plotly figure object containing only the centered message with
            invisible axes and white background.
    """
    fig = go.Figure()
    fig.add_annotation(
        text=message,
        xref="paper",
        yref="paper",
        x=0.5,
        y=0.5,
        showarrow=False,
        font=dict(size=18, color="gray"),
        align="center",
    )
    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=0, r=0, t=40, b=0),
    )
    return fig
