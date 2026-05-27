from datetime import date

import pandas as pd
import streamlit as st

from dashboard.data import (
    countries_for_regions,
    default_reference_date,
    default_time_series_range,
    get_region_country_map,
    normalize_date_range,
)
from dashboard.metrics import METRICS, Metric
from dashboard.settings import SIDEBAR_LOGO


def render_sidebar_logo() -> None:
    if SIDEBAR_LOGO.exists():
        st.image(SIDEBAR_LOGO, width="stretch")


def render_sidebar_common_filters(df: pd.DataFrame) -> tuple[list[str], list[str], list[str]]:
    region_map = get_region_country_map(df)
    all_regions = sorted(df["nam_region_short"].dropna().unique())
    all_brands = sorted(df["nam_brand_short"].dropna().unique())

    st.subheader("Filters")

    regions = st.multiselect("Region", all_regions, key="filter_regions")
    brands = st.multiselect("Brand", all_brands, key="filter_brands")
    available_countries = countries_for_regions(df, regions, region_map)
    countries = st.multiselect("Country", available_countries, key="filter_countries")
    countries = [country for country in countries if country in available_countries]

    return brands, regions, countries


def render_sidebar_overview_date(df: pd.DataFrame) -> date:
    st.subheader("Overview")
    min_date = df["dat_load"].min().date()
    max_date = df["dat_load"].max().date()
    return st.date_input(
        "Date",
        value=default_reference_date(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="filter_overview_date",
    )


def render_sidebar_time_series_dates(df: pd.DataFrame) -> tuple[date, date]:
    st.subheader("Time series")
    min_date = df["dat_load"].min().date()
    max_date = df["dat_load"].max().date()
    default_start, default_end = default_time_series_range(min_date, max_date)

    start_date = st.date_input(
        "Start date",
        value=default_start,
        min_value=min_date,
        max_value=max_date,
        key="filter_start_date",
    )
    end_date = st.date_input(
        "End date",
        value=default_end,
        min_value=min_date,
        max_value=max_date,
        key="filter_end_date",
    )

    if start_date > end_date:
        st.warning("Start date was after end date — dates have been swapped.")
    return normalize_date_range(start_date, end_date)


def render_sidebar_alert_threshold() -> float:
    st.subheader("Alerts")
    return st.slider(
        "Alert threshold (%)",
        min_value=5,
        max_value=50,
        value=20,
        step=1,
        help="Flag rows when a delta exceeds this threshold in either direction.",
        key="alert_threshold",
    )


def render_sidebar_metrics() -> list[Metric]:
    st.subheader("Metrics")
    selected_metric_keys = st.multiselect(
        "Metrics",
        options=list(METRICS.keys()),
        default=["traffic"],
        format_func=lambda key: METRICS[key].label,
        key="time_series_metrics",
        label_visibility="collapsed",
    )
    return [METRICS[key] for key in selected_metric_keys]
