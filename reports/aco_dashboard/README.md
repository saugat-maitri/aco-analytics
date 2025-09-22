# <img src="../../assets/tuva_health_logo.png" width="200"/>   ACO Dashboard

This module implements the main Accountable Care Organization (ACO) analytics dashboard for the TUVA Health project.

---

## 📊 Features:
- Population health metrics tracking and visualization
- Cost and utilization trend analysis across time periods
- Risk-adjusted performance measures
- Patient demographic breakdowns and filters
- Provider network analytics and benchmarking

---

## 📁 Folder Structure

```
aco_dashboard/
├── __init__.py
├── callbacks.py    # Callback logic for dashboard interactivity
├── data.py         # Dashboard data aggregation and query logic
├── layout.py       # Dashboard layout and component arrangement
```

---

## 📄 Key Files

- **callbacks.py**  
    Contains all Dash callback functions for user interactivity, filtering and dynamic updates.

- **data.py**  
    Provides data access and aggregation functions for KPIs, trends, demographics and cohort analysis. All SQL queries and data wrangling for the dashboard are here.

- **layout.py**  
    Defines the dashboard's layout, including arrangement of charts, KPI cards and filters.

---

## 🚀 Usage
- This dashboard is loaded as part of the main Dash app.  
- All callbacks and data logic are encapsulated in this module for maintainability.
- Select a date range and comparison period to update all KPIs and trend graphs.
- All data is loaded from data warehouse.
- The updated data is reflected on all the graphs components. 

---

## 🔧 Extending

To add new features or visualizations:
- Add new data queries to `data.py`
- Add new callbacks to `callbacks.py`
- Update the layout in `layout.py`

---

## 📧 Contact

For questions or contributions, please open an issue or pull request in the main repository.
