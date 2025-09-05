def dt_to_yyyymm(dt):
    return dt.year * 100 + dt.month


def extract_sql_filters(group_click=None, encounter_type_click=None, ccsr_click=None):
    """Extract SQL filters from the selected data points."""
    filters = {}
    if group_click and group_click.get("points"):
        filters["ENCOUNTER_GROUP"] = group_click["points"][0]["y"]
    if encounter_type_click and encounter_type_click.get("points"):
        filters["ENCOUNTER_TYPE"] = encounter_type_click["points"][0]["y"]
    if ccsr_click and ccsr_click.get("points"):
        filters["CCSR_CATEGORY_DESCRIPTION"] = ccsr_click["points"][0]["customdata"]
    return filters


# Truncate long text
def truncate_text(text, max_length=30):
    return text[:max_length] + "..." if len(text) > max_length else text
