from datetime import date

import pandas as pd
import streamlit as st

from dashboard.metrics import (
    HIDDEN_COLUMNS,
    METRICS,
    aggregate_metric,
    build_alerts_table,
    build_metric_table,
    format_metric_value,
    get_snapshot,
    kpi_delta_label,
    style_alerts_table,
    style_metric_table,
)
from dashboard.settings import ALERT_GREEN, ALERT_RED, TABLE_HEIGHT


def render_styled_dataframe(styler) -> None:
    st.dataframe(
        styler,
        width="stretch",
        hide_index=True,
        height=TABLE_HEIGHT,
    )


def render_data_freshness_banner(latest_data_date: date) -> None:
    today = date.today()
    if latest_data_date >= today:
        return

    days_behind = (today - latest_data_date).days
    day_label = "day" if days_behind == 1 else "days"
    st.info(
        f"Latest available data: **{latest_data_date:%Y-%m-%d}** "
        f"({days_behind} {day_label} behind today)."
    )


def render_kpis(df: pd.DataFrame) -> None:
    count_metrics = [m for m in METRICS.values() if m.format == "count"]
    bounce = METRICS["bounce_rate"]

    cols = st.columns(len(count_metrics) + 1)
    for col, metric in zip(cols, count_metrics):
        col.metric(
            metric.label,
            format_metric_value(aggregate_metric(df, metric), metric),
            delta=kpi_delta_label(df, metric),
        )

    cols[-1].metric(
        bounce.label,
        format_metric_value(aggregate_metric(df, bounce), bounce),
        delta=kpi_delta_label(df, bounce),
    )


def render_alert_summary(snapshot: pd.DataFrame, threshold: float) -> None:
    alerts = build_alerts_table(snapshot, threshold)
    if alerts.empty:
        st.success(f"No alerts — all deltas are within ±{threshold:.0f}%.")
        return

    combination_count = alerts[["Region", "Brand", "Country"]].drop_duplicates().shape[0]
    st.warning(
        f"{len(alerts)} alert{'s' if len(alerts) != 1 else ''} across "
        f"{combination_count} combination{'s' if combination_count != 1 else ''} "
        f"breaching ±{threshold:.0f}%."
    )
    with st.expander("View alert details"):
        render_styled_dataframe(style_alerts_table(alerts, threshold, ALERT_GREEN, ALERT_RED))


def render_overview_tab(filtered: pd.DataFrame, threshold: float) -> None:
    render_kpis(filtered)
    st.divider()

    snapshot_date = filtered["dat_load"].max()
    snapshot = get_snapshot(filtered, snapshot_date)
    st.caption(f"Monitoring snapshot for **{snapshot_date.strftime('%Y-%m-%d')}**.")

    render_alert_summary(snapshot, threshold)
    st.divider()

    st.subheader("Metric breakdown")
    metric_tabs = st.tabs([metric.label for metric in METRICS.values()])
    for tab, metric in zip(metric_tabs, METRICS.values()):
        with tab:
            table = build_metric_table(snapshot, metric)
            render_styled_dataframe(
                style_metric_table(table, metric, threshold, ALERT_GREEN, ALERT_RED)
            )

    st.divider()

    display_cols = [col for col in snapshot.columns if col not in HIDDEN_COLUMNS]
    export_df = snapshot[display_cols].sort_values(
        ["nam_region_short", "nam_brand_short", "nam_country_short"]
    )
    st.download_button(
        "Download snapshot CSV",
        data=export_df.to_csv(index=False).encode("utf-8"),
        file_name=f"monitoring_snapshot_{snapshot_date:%Y-%m-%d}.csv",
        mime="text/csv",
    )

    with st.expander("View raw data"):
        raw_df = filtered[[col for col in filtered.columns if col not in HIDDEN_COLUMNS]].sort_values(
            ["dat_load", "nam_region_short", "nam_brand_short", "nam_country_short"],
            ascending=False,
        )
        st.dataframe(
            raw_df,
            width="stretch",
            hide_index=True,
            height=TABLE_HEIGHT,
        )
        st.download_button(
            "Download filtered raw data CSV",
            data=raw_df.to_csv(index=False).encode("utf-8"),
            file_name=f"raw_data_{snapshot_date:%Y-%m-%d}.csv",
            mime="text/csv",
            key="download_raw_data",
        )
