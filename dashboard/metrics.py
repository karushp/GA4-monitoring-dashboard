from dataclasses import dataclass

import pandas as pd
from pandas.io.formats.style import Styler

DISPLAY_DIMS = ["Region", "Brand", "Country"]
DELTA_YESTERDAY = "Δ vs yesterday"
DELTA_WEEKLY = "Δ vs weekly"
HIDDEN_COLUMNS = {"status", "status_traffic", "status_purchase"}


@dataclass(frozen=True)
class Metric:
    key: str
    label: str
    today: str
    yesterday: str
    weekly_avg: str
    pct_yesterday: str | None
    pct_weekly: str | None
    agg: str  # "sum" or "mean"
    format: str  # "count" or "percent"


METRICS: dict[str, Metric] = {
    "traffic": Metric(
        key="traffic",
        label="Traffic",
        today="today_traffic",
        yesterday="yesterday_traffic",
        weekly_avg="weekly_avg_traffic",
        pct_yesterday="pct_vs_yesterday_traffic",
        pct_weekly="pct_vs_weekly_traffic",
        agg="sum",
        format="count",
    ),
    "purchase": Metric(
        key="purchase",
        label="Purchases",
        today="today_purchase",
        yesterday="yesterday_purchase",
        weekly_avg="weekly_avg_purchase",
        pct_yesterday="pct_vs_yesterday_purchase",
        pct_weekly="pct_vs_weekly_purchase",
        agg="sum",
        format="count",
    ),
    "add_to_cart": Metric(
        key="add_to_cart",
        label="Add to cart",
        today="today_add_to_cart",
        yesterday="yesterday_add_to_cart",
        weekly_avg="weekly_avg_add_to_cart",
        pct_yesterday="pct_vs_yesterday_atc",
        pct_weekly="pct_vs_weekly_atc",
        agg="sum",
        format="count",
    ),
    "page_views": Metric(
        key="page_views",
        label="Page views",
        today="today_page_view",
        yesterday="yesterday_page_view",
        weekly_avg="weekly_avg_page_view",
        pct_yesterday="pct_vs_yesterday_pv",
        pct_weekly="pct_vs_weekly_pv",
        agg="sum",
        format="count",
    ),
    "bounce_rate": Metric(
        key="bounce_rate",
        label="Bounce rate",
        today="today_bounce_rate_pct",
        yesterday="yesterday_bounce_rate_pct",
        weekly_avg="weekly_avg_bounce_rate_pct",
        pct_yesterday="diff_vs_yesterday_bounce_rate",
        pct_weekly="diff_vs_weekly_bounce_rate",
        agg="mean",
        format="percent",
    ),
}


def aggregate_metric(df, metric: Metric):
    if metric.agg == "sum":
        return df[metric.today].sum()
    return df[metric.today].mean()


def format_metric_value(value: float, metric: Metric) -> str:
    if metric.format == "percent":
        return f"{value:.2f}%"
    return f"{value:,.0f}"


def kpi_delta_label(df, metric: Metric) -> str | None:
    if df.empty:
        return None

    if metric.format == "percent":
        today = df[metric.today].mean()
        yesterday = df[metric.yesterday].mean()
        if pd.isna(today) or pd.isna(yesterday):
            return None
        return f"{today - yesterday:+.2f} pp"

    today = df[metric.today].sum()
    yesterday = df[metric.yesterday].sum()
    if pd.isna(today) or pd.isna(yesterday) or yesterday == 0:
        return None
    pct = (today - yesterday) / yesterday * 100
    return f"{pct:+.1f}%"


def get_snapshot(df: pd.DataFrame, snapshot_date: pd.Timestamp | None = None) -> pd.DataFrame:
    if df.empty:
        return df.copy()
    date = snapshot_date or df["dat_load"].max()
    return df[df["dat_load"] == date].copy()


def higher_is_better(metric: Metric) -> bool:
    return metric.key != "bounce_rate"


def breaches_threshold(value: float, threshold: float, metric: Metric) -> bool:
    if pd.isna(value):
        return False
    return value >= threshold or value <= -threshold


def delta_style(value: float, threshold: float, metric: Metric, green: str, red: str) -> str:
    if pd.isna(value):
        return ""
    if higher_is_better(metric):
        if value >= threshold:
            return f"background-color: {green}; color: #1A1A1A"
        if value <= -threshold:
            return f"background-color: {red}; color: #1A1A1A"
    else:
        if value >= threshold:
            return f"background-color: {red}; color: #1A1A1A"
        if value <= -threshold:
            return f"background-color: {green}; color: #1A1A1A"
    return ""


def format_delta(value: float, metric: Metric) -> str:
    if pd.isna(value):
        return ""
    if metric.format == "percent":
        return f"{value:+.2f} pp"
    return f"{value:+.2f}%"


def format_value(value: float, metric: Metric) -> str:
    if pd.isna(value):
        return ""
    if metric.format == "percent":
        return f"{value:.2f}%"
    return f"{value:,.0f}"


def build_metric_table(snapshot: pd.DataFrame, metric: Metric) -> pd.DataFrame:
    columns = [*DISPLAY_DIMS, "Today", "Yesterday", DELTA_YESTERDAY, DELTA_WEEKLY]
    if snapshot.empty:
        return pd.DataFrame(columns=columns)

    table = pd.DataFrame(
        {
            "Region": snapshot["nam_region_short"],
            "Brand": snapshot["nam_brand_short"],
            "Country": snapshot["nam_country_short"],
            "Today": snapshot[metric.today],
            "Yesterday": snapshot[metric.yesterday],
            DELTA_YESTERDAY: snapshot[metric.pct_yesterday],
            DELTA_WEEKLY: snapshot[metric.pct_weekly],
        }
    )

    if metric.key == "bounce_rate":
        return table.sort_values(DELTA_YESTERDAY, ascending=False, na_position="last")
    return table.sort_values(DELTA_YESTERDAY, ascending=True, na_position="last")


def style_metric_table(
    table: pd.DataFrame,
    metric: Metric,
    threshold: float,
    green: str,
    red: str,
) -> Styler:
    styler = table.style

    for col in [DELTA_YESTERDAY, DELTA_WEEKLY]:
        styler = styler.map(
            lambda value, metric=metric: delta_style(value, threshold, metric, green, red),
            subset=col,
        )

    return styler.format(
        {
            "Today": lambda value: format_value(value, metric),
            "Yesterday": lambda value: format_value(value, metric),
            DELTA_YESTERDAY: lambda value: format_delta(value, metric),
            DELTA_WEEKLY: lambda value: format_delta(value, metric),
        }
    )


def build_alerts_table(snapshot: pd.DataFrame, threshold: float) -> pd.DataFrame:
    columns = ["Region", "Brand", "Country", "Metric", DELTA_YESTERDAY, DELTA_WEEKLY, "_metric_key"]
    if snapshot.empty:
        return pd.DataFrame(columns=columns)

    alerts: list[dict] = []
    for _, row in snapshot.iterrows():
        for metric in METRICS.values():
            delta_y = row.get(metric.pct_yesterday)
            delta_w = row.get(metric.pct_weekly)
            if not breaches_threshold(delta_y, threshold, metric) and not breaches_threshold(
                delta_w, threshold, metric
            ):
                continue

            alerts.append(
                {
                    "Region": row["nam_region_short"],
                    "Brand": row["nam_brand_short"],
                    "Country": row["nam_country_short"],
                    "Metric": metric.label,
                    DELTA_YESTERDAY: delta_y,
                    DELTA_WEEKLY: delta_w,
                    "_metric_key": metric.key,
                }
            )

    if not alerts:
        return pd.DataFrame(columns=columns)

    return pd.DataFrame(alerts).sort_values(DELTA_YESTERDAY, ascending=True, na_position="last")


def style_alerts_table(
    alerts: pd.DataFrame,
    threshold: float,
    green: str,
    red: str,
) -> Styler:
    display_cols = ["Region", "Brand", "Country", "Metric", DELTA_YESTERDAY, DELTA_WEEKLY]
    if alerts.empty:
        return pd.DataFrame(columns=display_cols).style

    display = alerts[display_cols].copy()
    display[DELTA_YESTERDAY] = display[DELTA_YESTERDAY].astype(object)
    display[DELTA_WEEKLY] = display[DELTA_WEEKLY].astype(object)
    for index, row in alerts.iterrows():
        metric = METRICS[row["_metric_key"]]
        display.at[index, DELTA_YESTERDAY] = format_delta(row[DELTA_YESTERDAY], metric)
        display.at[index, DELTA_WEEKLY] = format_delta(row[DELTA_WEEKLY], metric)

    def highlight_row(row: pd.Series) -> list[str]:
        metric = METRICS[alerts.loc[row.name, "_metric_key"]]
        styles = []
        for column in display_cols:
            if column in (DELTA_YESTERDAY, DELTA_WEEKLY):
                delta_value = alerts.loc[row.name, column]
                styles.append(delta_style(delta_value, threshold, metric, green, red))
            else:
                styles.append("")
        return styles

    return display.style.apply(highlight_row, axis=1)
