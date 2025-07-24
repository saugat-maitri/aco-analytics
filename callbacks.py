from dash import Input, Output, callback
import pandas as pd

@callback(
    Output("year-dropdown", "options"),
    Input("year-dropdown", "value")
)
def populate_years(_):
    df = pd.read_csv("data/outlier_member_months.csv")
    unique_years = sorted(df["YEAR"].unique())
    return [{"label": str(year), "value": year} for year in unique_years]