
import plotly.graph_objs as go


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
    """Return a vertical bar chart."""
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
        x=x, # Accepts the pandas data series
        y=y, # Accepts the pandas data series
        orientation='v',
        marker_color=colors,
        text=text, # Text displays for each bar and can be seen on bar hover
        textposition=textposition, # Define where to display the text, inside or outside the bar
        hovertemplate=hovertemplate, # Defines how to display the hover information
        customdata=custom, # It is used as source data for hovertemplate
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
    """Return a horizontal bar chart."""
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
        x=x, # Accepts the pandas data series
        y=y, # Accepts the pandas data series
        orientation='h',
        marker_color=colors,
        text=text, # Text displays for each bar and can be seen on bar hover
        textposition=textposition, # Define where to display the text, inside or outside the bar
        hovertemplate=hovertemplate, # Defines how to display the hover information
        customdata=custom, # It is used as source data for hovertemplate
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