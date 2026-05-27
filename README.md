# Data Monitor Dashboard

Streamlit dashboard for monitoring GA4 traffic.

**Current data source:** CSV files from the `data/` folder (configured in `dashboard/settings.py`). The app loads all `*.csv` files on startup — no database or API connection yet.

**Planned enhancement:** direct BigQuery integration to query live GA4 data instead of relying on exported files.

## Features

**Overview**
- KPI scorecards with day-over-day deltas
- Alert summary when metric changes exceed a configurable threshold
- Per-metric breakdown tables (Region → Brand → Country)
- Snapshot and raw data CSV export

**Time series**
- Line charts per region · brand · country combination
- Multi-metric overlay with bounce rate on a secondary axis
- Paginated charts (10 per page) over a configurable date range

**Sidebar**
- Filter by region, brand, and country
- Tab-specific controls (overview date, time series range, alert threshold, metrics)
- Theme and chart colors from `.streamlit/color.json`

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended)

## Setup

```bash
uv sync
```

Copy `.env.example` to `.env` and set your dashboard credentials:

```bash
cp .env.example .env
```

| Variable | Description |
|----------|-------------|
| `username` | Sign-in username (also accepts `DASHBOARD_USERNAME`) |
| `password` | Sign-in password (also accepts `DASHBOARD_PASSWORD`) |

`.env` is gitignored. Do not commit real credentials.

## Run

```bash
uv run streamlit run app.py
```

## Project layout

```
app.py                 # Streamlit entry point (page config + tab wiring)
dashboard/             # Application code (no src/ folder)
  auth.py              # Env-based login gate
  settings.py          # Paths and constants
  data.py              # CSV loading, filters, date helpers
  metrics.py           # Metric definitions, KPIs, alert tables
  theme.py             # CSS, Plotly styling, chart builder
  sidebar.py           # Sidebar controls
  overview.py          # Overview tab
  time_series.py       # Time series tab
data/                  # CSV input files
img/                   # Optional sidebar logo (Union.jpg)
.streamlit/
  config.toml          # Streamlit server/theme config
  color.json           # Brand and chart colors
```

`app.py` stays thin: it loads data, renders the sidebar, and delegates each tab to `dashboard/overview.py` and `dashboard/time_series.py`.

## Data

The app reads from the `data/` folder by default. To use a different location, update `DATA_DIR` in `dashboard/settings.py`.

Place one or more `*.csv` files there. The app loads and merges them on startup, deduplicating by date and region/brand/country.

Expected columns include traffic, purchase, add to cart, page view, and bounce rate metrics (`today_*`, `yesterday_*`, `weekly_avg_*`, and comparison columns). Status columns are loaded but hidden in the UI.

Each row should include:

| Column | Description |
|--------|-------------|
| `dat_load` | Snapshot date |
| `nam_region_short` | Region |
| `nam_brand_short` | Brand |
| `nam_country_short` | Country |

## Configuration

- **Data folder** — `DATA_DIR` in `dashboard/settings.py` (default: `data/`)
- **Alert threshold** — adjustable in the sidebar (default ±20%)
- **Time series range** — defaults to the last 90 days ending on today (or the latest available date)
- **Colors** — edit `.streamlit/color.json` to change brand and chart palette

## Future enhancements

- **BigQuery integration** — connect directly to BigQuery to pull GA4 metrics on demand, replacing manual CSV exports
