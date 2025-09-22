
# <img src="assets/tuva_health_logo.png" width="200"/>   TUVA Analytics Dash Application

A modular Dash web application for monitoring and analyzing healthcare data. The platform supports multiple dashboards, each tailored to a specific analytical or reporting purpose (such as ACO analytics).

---

## 📊 Features
- Modular dashboard architecture for different healthcare analytics needs
- Customizable visualizations and reports
- User-friendly interface for healthcare professionals and analysts
- Secure integration with Snowflake for scalable data access

---

## 📁 Project Structure

```
aco-analytics/
├── app.py                       # Dash app entry point
├── layouts.py                   # App layout and UI components
├── components/                  # Reusable Dash/Plotly components
│   ├── bar_chart.py             # Vertical, horizontal, and stacked bar charts
│   ├── box_plot.py              # Box plot component
│   ├── demographics_card.py     # Demographics summary card
│   ├── header.py                # App header
│   ├── kpi_card.py              # KPI card component
│   ├── no_data_figure.py        # Empty state figure
│   └── trend_chart.py           # Trend chart component
├── services/                    # Data and utility services
│   ├── database.py              # Snowflake connection logic
│   ├── queries.py               # SQL queries
│   └── utils.py                 # Utility functions (date, formatting, SQL filters)
├── reports/                     # Report modules (e.g., dashboards, callbacks, data logic)
│   └── aco_dashboard/           # Main dashboard and all callback/data logic
│       ├── __init__.py
│       ├── callbacks.py         # Callback logic of ACO Dashboard
│       ├── data.py              # Dashboard data aggregation and query logic
│       └── layout.py            # ACO Dashboard layout
├── csv_sample/                  # Sample CSVs for local testing
│   ├── DIM_ENCOUNTER_GROUP.csv
│   ├── DIM_ENCOUNTER_TYPE.csv
│   ├── DIM_MEMBER.csv
│   ├── FACT_CLAIMS.csv
│   └── FACT_MEMBER_MONTHS.csv
├── assets/                      # Static assets (CSS, images)
│   ├── custom.css
│   └── tuva_health_logo.png
├── .env                         # Snowflake credentials (not committed)
└── requirements.txt             # Python dependencies
```

---

## 🚀 Setup & Installation

1. **Set up Python environment:**
   ```bash
   # Create virtual environment
   python -m venv venv

   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

2. **Clone the repository:**
   ```bash
   git clone https://github.com/saugat-maitri/aco-analytics
   cd aco-analytics
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure your `.env` file with Snowflake credentials (see `.env.example`):**
   ```env
   SNOWFLAKE_AUTH_METHOD=externalbrowser (or password)
   SNOWFLAKE_USER=your_user
   SNOWFLAKE_ACCOUNT=your_account
   SNOWFLAKE_DATABASE=your_db
   SNOWFLAKE_SCHEMA=your_schema
   SNOWFLAKE_WAREHOUSE=your_warehouse
   SNOWFLAKE_ROLE=your_role
   # SNOWFLAKE_PASSWORD=your_password (if not using externalbrowser)
   ```

5. **Run the app:**
   ```bash
   python app.py
   ```

---

## 🛠️ Key Utility Functions

The `services/utils.py` module provides reusable helpers for date formatting, SQL filter extraction, and comparison period calculations.  
**Examples:**

- `dt_to_yyyymm(dt)`: Convert a `datetime` to `YYYYMM` integer.
- `extract_sql_filters(...)`: Extracts SQL filters from chart click events.
- `build_filter_clause(filters)`: Builds SQL WHERE clauses from filter dictionaries.
- `format_large_number(value)`: Formats numbers with `$` and K/M/B suffixes.
