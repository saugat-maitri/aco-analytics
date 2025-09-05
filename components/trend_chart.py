import plotly.graph_objects as go


def trend_chart(current_data, comparison_data):
    fig = go.Figure()

    if current_data:
        x_cur, y_cur = zip(*current_data)
        fig.add_trace(
            go.Scatter(
                x=x_cur,
                y=y_cur,
                mode="lines+markers",
                name="Current",
                line=dict(color="#64b0e1"),
            )
        )

    if comparison_data:
        x_cmp, y_cmp = zip(*comparison_data)
        fig.add_trace(
            go.Scatter(
                x=x_cmp,
                y=y_cmp,
                mode="lines+markers",
                name="Comparison",
                line=dict(color="gray", dash="dash"),
            )
        )

    fig.update_layout(
        margin=dict(l=20, r=20, t=30, b=30),
        plot_bgcolor="white",
        height=100,
        hovermode="x unified",
        showlegend=False,
    )

    return fig
