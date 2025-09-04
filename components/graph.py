
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
        xref="paper", yref="paper",
        x=0.5, y=0.5,
        showarrow=False,
        font=dict(size=18, color="gray"),
        align="center"
    )
    fig.update_layout(
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor="white",
        paper_bgcolor="white",
        margin=dict(l=0, r=0, t=40, b=0),
    )
    return fig


def vertical_bar_chart(
    x,
    y,
    color_fn=None,
    text_fn=None,
    margin=None,
    marker_color=None,
    showticklabels=True,
    plot_bgcolor='white',
    clickmode='event+select',
    customdata=None,
    textposition='outside',
    hovertemplate=None
):
    """Create and return a vertical bar chart using plotly.

    Args:
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

    Returns:
        plotly.graph_objects.Figure: A plotly vertical bar chart figure.

    Notes:
        - Chart height is dynamically calculated based on number of bars
        - Minimum height is 200px
        - Bar height is fixed at 40px
        - Y-axis range is automatically set to 110% of maximum y value
        - Handles empty data gracefully.
    """
    colors = color_fn(y) if color_fn else marker_color
    text = text_fn(y) if text_fn else y
    custom = customdata if customdata is not None else y if hasattr(y, "empty") else None
    
    if hasattr(y, "empty"):
        max_value = max(y) if not y.empty else 0
        n_bars = len(y) if not y.empty else 1
    else:
        max_value = max(y) if y else 0
        n_bars = len(y) if y else 1
    y_range_max = max_value * 1.1 if max_value > 0 else 1
    bar_height = 40
    min_height = 200
    fig_height = max(min_height, n_bars * bar_height + 100) # Define the height of the bar to maintain the proper height of graph

    fig = go.Figure(go.Bar(
        x=x,
        y=y,
        orientation='v',
        marker_color=colors,
        text=text,
        textposition=textposition,
        hovertemplate=hovertemplate,
        customdata=custom,
    ))
    fig.update_layout(
        margin=margin or dict(l=20, r=20, t=20, b=20),  
        xaxis=dict(automargin=True),          
        yaxis=dict(showticklabels=showticklabels, range=[0, y_range_max]),
        plot_bgcolor=plot_bgcolor,
        clickmode=clickmode,
        height=fig_height
    )
    return fig

def horizontal_bar_chart(
    x,
    y,
    color_fn=None,
    text_fn=None,
    margin=None,
    marker_color=None,
    showticklabels=True,
    plot_bgcolor='white',
    clickmode='event+select',
    customdata=None,
    textposition='outside',
    hovertemplate=None
):
    """Create and return a horizontal bar chart using plotly.

    Args:
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

    Returns:
        plotly.graph_objs.Figure: A horizontal bar chart figure object.

    Notes:
        - The chart height adjusts automatically based on the number of bars
        - Bars are displayed in reversed order (top to bottom)
        - The x-axis range extends 10% beyond the maximum value
    """
    colors = color_fn(x) if color_fn else marker_color # Use color function if provided for the individual bar
    text = text_fn(x) if text_fn else x # Define the text to display on each bar
    custom = customdata if customdata is not None else y # Use custom data if provided, else use y values fot the text
    
    if hasattr(x, "empty"):
        max_value = max(x) if not x.empty else 0
        n_bars = len(x) if not x.empty else 1
    else:
        max_value = max(x) if x else 0
        n_bars = len(x) if x else 1
    x_range_max = max_value * 1.1 if max_value > 0 else 1
    bar_height = 20
    min_height = 200
    fig_height = max(min_height, n_bars * bar_height + 100) # Define the height of the bar to maintain the proper height of graph
    
    fig = go.Figure(go.Bar(
        x=x,
        y=y,
        orientation='h',
        marker_color=colors,
        text=text,
        textposition=textposition,
        hovertemplate=hovertemplate,
        customdata=custom,
    ))
    fig.update_layout(
        margin=margin or dict(l=20, r=20, t=0, b=0),
        yaxis=dict(autorange="reversed"),
        xaxis=dict(showticklabels=showticklabels, range=[0, x_range_max]),
        plot_bgcolor=plot_bgcolor,
        clickmode=clickmode,
        height=fig_height,
    )
    return fig