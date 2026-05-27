import pandas as pd
import streamlit as st

from dashboard.metrics import Metric
from dashboard.settings import TIME_SERIES_CHARTS_PER_PAGE
from dashboard.theme import ThemeColors, build_time_series_figure, series_label


def get_chart_page(total_pages: int) -> int:
    if "time_series_page" not in st.session_state:
        st.session_state.time_series_page = 1

    st.session_state.time_series_page = max(
        1, min(st.session_state.time_series_page, total_pages)
    )
    return st.session_state.time_series_page


def render_chart_pagination(total_pages: int) -> None:
    get_chart_page(total_pages)

    st.caption("Chart page")
    prev_col, page_col, next_col = st.columns([1, 2, 1], gap="small")
    with prev_col:
        if st.button(
            "<",
            disabled=st.session_state.time_series_page <= 1,
            key="time_series_page_prev",
            width="stretch",
        ):
            st.session_state.time_series_page -= 1
            st.rerun()
    with page_col:
        st.markdown(
            f"<div style='text-align: center; padding-top: 0.35rem;'>"
            f"{st.session_state.time_series_page} / {total_pages}"
            f"</div>",
            unsafe_allow_html=True,
        )
    with next_col:
        if st.button(
            ">",
            disabled=st.session_state.time_series_page >= total_pages,
            key="time_series_page_next",
            width="stretch",
        ):
            st.session_state.time_series_page += 1
            st.rerun()


def render_time_series_tab(
    df: pd.DataFrame,
    selected_metrics: list[Metric],
    theme: ThemeColors,
) -> None:
    st.markdown(
        f'<p style="font-size: 1.25rem; font-weight: 600; color: {theme.primary_bright}; '
        f'margin-bottom: 0.25rem;">Metric time series</p>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Each matching region, brand, and country combination gets its own chart. "
        "Choose metrics in the sidebar."
    )

    if not selected_metrics:
        st.warning("Select at least one metric in the sidebar.")
        return

    if df.empty:
        st.warning("No data matches the selected filters.")
        return

    series_keys = (
        df[["nam_brand_short", "nam_region_short", "nam_country_short"]]
        .drop_duplicates()
        .sort_values(["nam_region_short", "nam_brand_short", "nam_country_short"])
        .reset_index(drop=True)
    )

    if series_keys.empty:
        st.warning("No time series available for the current selection.")
        return

    total_charts = len(series_keys)
    total_pages = max(
        1, (total_charts + TIME_SERIES_CHARTS_PER_PAGE - 1) // TIME_SERIES_CHARTS_PER_PAGE
    )
    page = get_chart_page(total_pages)
    start_idx = (page - 1) * TIME_SERIES_CHARTS_PER_PAGE
    end_idx = start_idx + TIME_SERIES_CHARTS_PER_PAGE
    page_keys = series_keys.iloc[start_idx:end_idx]

    st.info(
        f"Showing charts {start_idx + 1}–{min(end_idx, total_charts)} of {total_charts} "
        f"(page {page} of {total_pages})."
    )

    for _, row in page_keys.iterrows():
        brand = row["nam_brand_short"]
        region = row["nam_region_short"]
        country = row["nam_country_short"]

        plot_df = df[
            (df["nam_brand_short"] == brand)
            & (df["nam_region_short"] == region)
            & (df["nam_country_short"] == country)
        ]

        fig = build_time_series_figure(
            plot_df,
            selected_metrics,
            series_label(region, brand, country),
            theme,
        )
        st.plotly_chart(fig, width="stretch")

    st.divider()
    render_chart_pagination(total_pages)
