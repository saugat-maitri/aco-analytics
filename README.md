# TUVA Health ACO Analytics

Dash web application for analyzing Accountable Care Organization (ACO) claims and member data. It provides interactive KPIs, trends, and cost driver visualizations, powered by data from Snowflake.

## Features
- Dynamic KPI cards (PMPM Cost, Utilization, Cost Per Encounter) based on user-selected date ranges and comparison periods
- Interactive trend graphs for PMPM, Utilization (PKPY), and Cost Per Encounter
- Cost drivers and risk distribution visualizations
- Modular callback structure for maintainability
- Snowflake integration

## Project Structure

```
aco-analytics/
├── app.py                # Dash app entry point
├── layouts.py            # App layout and UI components
├── components.py         # Reusable Dash/Bootstrap components
├── data.py               # Data loading and Snowflake connection logic
├── utils.py              # Utility functions
├── callbacks/
│   ├── __init__.py
│   ├── kpi.py            # KPI card callbacks
│   └── trends.py         # Trend graph callbacks
├── data/               # Used for testing (will be removed)
│   ├── 
├── assets/               # Static assets (CSS, images)
│   ├── custom.css
│   └── tuva_health_logo.png
├── .env                  # Snowflake credentials (not committed)
└── requirements.txt      # Python dependencies
```

## Setup & Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/saugat-maitri/aco-analytics
   cd aco-analytics
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure your `.env` file with Snowflake credentials (see `.env.example`):
   ```env
   SNOWFLAKE_AUTH_METHOD=externalbrowser
   SNOWFLAKE_USER=your_user
   SNOWFLAKE_ACCOUNT=your_account
   SNOWFLAKE_DATABASE=your_db
   SNOWFLAKE_SCHEMA=your_schema
   SNOWFLAKE_WAREHOUSE=your_warehouse
   SNOWFLAKE_ROLE=your_role
   # SNOWFLAKE_PASSWORD=your_password (if not using externalbrowser)
   ```
4. Run the app:
   ```bash
   python app.py
   ```

## Usage
- Select a date range and comparison period to update all KPIs and trend graphs.
- All data is loaded from data warehouse.
- The app is modular: callbacks are organized by feature in the `callbacks/` folder.
