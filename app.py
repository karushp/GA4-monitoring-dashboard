import streamlit as st

from dashboard.data import apply_filters, get_data, list_data_files
from dashboard.overview import render_data_freshness_banner, render_overview_tab
from dashboard.settings import DATA_DIR, PAGE_ICON, PAGE_TITLE
from dashboard.sidebar import (
    render_sidebar_alert_threshold,
    render_sidebar_common_filters,
    render_sidebar_logo,
    render_sidebar_metrics,
    render_sidebar_overview_date,
    render_sidebar_time_series_dates,
)
from dashboard.theme import (
    apply_light_theme,
    configure_plotly_theme,
    install_sidebar_tab_sync,
)
from dashboard.time_series import render_time_series_tab

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout="wide",
)

THEME = apply_light_theme()
configure_plotly_theme(THEME)


def main() -> None:
    st.title(PAGE_TITLE)

    files = list_data_files()
    if not files:
        st.error(f"No CSV files found in `{DATA_DIR}`. Add data files to get started.")
        return

    with st.sidebar:
        render_sidebar_logo()
        df = get_data()
        if df.empty:
            st.warning("No rows loaded from data files.")
            return

        brands, regions, countries = render_sidebar_common_filters(df)
        overview_date = render_sidebar_overview_date(df)
        alert_threshold = render_sidebar_alert_threshold()
        time_series_range = render_sidebar_time_series_dates(df)
        selected_metrics = render_sidebar_metrics()

    latest_data_date = df["dat_load"].max().date()
    render_data_freshness_banner(latest_data_date)

    overview_filtered = apply_filters(
        df, brands, regions, countries, (overview_date, overview_date)
    )
    time_series_filtered = apply_filters(df, brands, regions, countries, time_series_range)

    overview_tab, time_series_tab = st.tabs(["Overview", "Time series"])

    with overview_tab:
        if overview_filtered.empty:
            st.warning("No data matches the selected filters.")
        else:
            render_overview_tab(overview_filtered, alert_threshold)

    with time_series_tab:
        render_time_series_tab(time_series_filtered, selected_metrics, THEME)

    install_sidebar_tab_sync()


if __name__ == "__main__":
    main()
