from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st

from dashboard.settings import DATA_DIR, TIME_SERIES_LOOKBACK_DAYS


def list_data_files() -> list[Path]:
    if not DATA_DIR.exists():
        return []
    return sorted(DATA_DIR.glob("*.csv"))


def load_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["dat_load"])
    return df.sort_values("dat_load")


def load_all_data() -> pd.DataFrame:
    files = list_data_files()
    if not files:
        return pd.DataFrame()

    frames = [load_csv(path) for path in files]
    combined = pd.concat(frames, ignore_index=True)
    combined = combined.drop_duplicates(
        subset=[
            "dat_load",
            "nam_brand_short",
            "nam_country_short",
            "nam_region_short",
        ],
        keep="last",
    )
    return combined.sort_values("dat_load")


@st.cache_data
def get_data() -> pd.DataFrame:
    return load_all_data()


@st.cache_data
def get_region_country_map(_df: pd.DataFrame) -> dict[str, list[str]]:
    return (
        _df.groupby("nam_region_short")["nam_country_short"]
        .apply(lambda series: sorted(series.dropna().unique()))
        .to_dict()
    )


def countries_for_regions(
    df: pd.DataFrame,
    regions: list[str],
    region_map: dict[str, list[str]],
) -> list[str]:
    if not regions:
        return sorted(df["nam_country_short"].dropna().unique())
    countries: set[str] = set()
    for region in regions:
        countries.update(region_map.get(region, []))
    return sorted(countries)


def apply_filters(
    df: pd.DataFrame,
    brands: list[str],
    regions: list[str],
    countries: list[str],
    date_range: tuple | None,
) -> pd.DataFrame:
    filtered = df.copy()
    if brands:
        filtered = filtered[filtered["nam_brand_short"].isin(brands)]
    if regions:
        filtered = filtered[filtered["nam_region_short"].isin(regions)]
    if countries:
        filtered = filtered[filtered["nam_country_short"].isin(countries)]
    if date_range:
        start, end = date_range
        filtered = filtered[
            (filtered["dat_load"] >= pd.Timestamp(start))
            & (filtered["dat_load"] <= pd.Timestamp(end))
        ]
    return filtered


def default_reference_date(min_date: date, max_date: date) -> date:
    today = date.today()
    if min_date <= today <= max_date:
        return today
    return max_date


def default_time_series_range(min_date: date, max_date: date) -> tuple[date, date]:
    end_date = default_reference_date(min_date, max_date)
    start_date = end_date - timedelta(days=TIME_SERIES_LOOKBACK_DAYS)
    if start_date < min_date:
        start_date = min_date
    return start_date, end_date


def normalize_date_range(start: date, end: date) -> tuple[date, date]:
    if start > end:
        return end, start
    return start, end
