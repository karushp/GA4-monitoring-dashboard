import json
from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from dashboard.metrics import Metric
from dashboard.settings import APP_ROOT

COLOR_FILE = APP_ROOT / ".streamlit" / "color.json"

DEFAULT_THEME = {
    "primaryBright": "#e20626",
    "primaryMedium": "#bf041d",
    "primaryDark": "#800010",
    "primaryDeep": "#4d000a",
    "background": "#ffffff",
    "text": "#1A1A1A",
    "secondaryBackground": "#FFF5F6",
    "border": "#F3D1D6",
}

DEFAULT_CHART_PALETTE = [
    "#f9c06d",
    "#fad6a5",
    "#97c147",
    "#bed986",
    "#e8707a",
    "#f297a5",
    "#4db1c6",
    "#9ad1d4",
]

DEFAULT_CHART = {
    "grid": "#e0e0e0",
    "palette": DEFAULT_CHART_PALETTE,
    "bounceRate": "#c4c4c4",
}


@dataclass(frozen=True)
class ChartColors:
    grid: str
    palette: tuple[str, ...]
    bounce_rate: str = "#c4c4c4"


@dataclass(frozen=True)
class ThemeColors:
    primary_bright: str
    primary_medium: str
    primary_dark: str
    primary_deep: str
    background: str
    text: str
    secondary_background: str
    border: str
    chart: ChartColors


def load_theme_colors() -> ThemeColors:
    theme = DEFAULT_THEME.copy()
    chart = DEFAULT_CHART.copy()

    if COLOR_FILE.exists():
        with COLOR_FILE.open() as file:
            payload = json.load(file)
        theme.update(payload.get("colors", {}))
        chart_config = payload.get("chart", {})
        chart["grid"] = chart_config.get("grid", chart["grid"])
        if "palette" in chart_config:
            chart["palette"] = chart_config["palette"]
        chart["bounceRate"] = chart_config.get("bounceRate", chart["bounceRate"])

    return ThemeColors(
        primary_bright=theme["primaryBright"],
        primary_medium=theme["primaryMedium"],
        primary_dark=theme["primaryDark"],
        primary_deep=theme["primaryDeep"],
        background=theme["background"],
        text=theme["text"],
        secondary_background=theme["secondaryBackground"],
        border=theme["border"],
        chart=ChartColors(
            grid=chart["grid"],
            palette=tuple(chart["palette"]),
            bounce_rate=chart["bounceRate"],
        ),
    )


def chart_palette(theme: ThemeColors | None = None) -> list[str]:
    colors = theme or load_theme_colors()
    return list(colors.chart.palette)


def metric_color_map(theme: ThemeColors | None = None) -> dict[str, str]:
    colors = theme or load_theme_colors()
    palette = list(colors.chart.palette)
    return {
        "traffic": palette[4],
        "purchase": palette[0],
        "add_to_cart": palette[2],
        "page_views": palette[6],
        "bounce_rate": colors.chart.bounce_rate,
    }


def apply_light_theme() -> ThemeColors:
    colors = load_theme_colors()
    css = f"""
    <style>
        :root {{
            color-scheme: light;
        }}

        .stApp,
        [data-testid="stAppViewContainer"],
        [data-testid="stHeader"],
        [data-testid="stToolbar"],
        [data-testid="stMainBlockContainer"],
        [data-testid="stSidebar"],
        [data-testid="stSidebarContent"],
        section[data-testid="stSidebar"] > div {{
            background-color: {colors.background} !important;
            color: {colors.text} !important;
        }}

        .stApp {{
            background-color: {colors.background} !important;
            color: {colors.text} !important;
        }}

        [data-testid="stSidebar"] {{
            border-right: 1px solid {colors.border};
        }}

        [data-testid="stMetricValue"] {{
            color: {colors.primary_dark} !important;
        }}

        div[data-testid="stTabs"] button[aria-selected="true"] {{
            color: {colors.primary_bright} !important;
            border-bottom-color: {colors.primary_bright} !important;
        }}

        [data-testid="stMultiSelect"] div[data-baseweb="select"],
        [data-testid="stSelectbox"] div[data-baseweb="select"] {{
            border: 1px solid {colors.border} !important;
            border-radius: 6px;
            box-shadow: none !important;
        }}

        [data-testid="stMultiSelect"] div[data-baseweb="select"] > div,
        [data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
            border: none !important;
            box-shadow: none !important;
            outline: none !important;
        }}

        [data-testid="stMultiSelect"] div[data-baseweb="select"]:focus-within,
        [data-testid="stSelectbox"] div[data-baseweb="select"]:focus-within {{
            border-color: {colors.primary_medium} !important;
            box-shadow: none !important;
        }}

        [data-testid="stDateInput"] div[data-baseweb="input"] {{
            border: 1px solid {colors.border} !important;
            border-radius: 6px;
            box-shadow: none !important;
        }}

        [data-testid="stDateInput"] div[data-baseweb="input"] input {{
            border: none !important;
            box-shadow: none !important;
            outline: none !important;
        }}

        [data-testid="stDateInput"] div[data-baseweb="input"]:focus-within {{
            border-color: {colors.primary_medium} !important;
            box-shadow: none !important;
        }}

        [data-testid="stSidebarUserContent"] {{
            font-size: 0.875rem;
        }}

        [data-testid="stSidebarUserContent"] [data-testid="stVerticalBlock"] {{
            gap: 0.35rem !important;
        }}

        [data-testid="stSidebarUserContent"] [data-testid="stVerticalBlockBorderWrapper"] {{
            padding-top: 0.15rem !important;
            padding-bottom: 0.15rem !important;
        }}

        [data-testid="stSidebarUserContent"] [data-testid="stHeading"] {{
            padding-top: 0.35rem !important;
            padding-bottom: 0.1rem !important;
        }}

        [data-testid="stSidebarUserContent"] h3 {{
            font-size: 0.85rem !important;
            line-height: 1.2 !important;
        }}

        [data-testid="stSidebarUserContent"] label,
        [data-testid="stSidebarUserContent"] [data-testid="stWidgetLabel"] p,
        [data-testid="stSidebarUserContent"] [data-testid="stMarkdownContainer"] p {{
            font-size: 0.82rem !important;
        }}

        [data-testid="stSidebarUserContent"] input,
        [data-testid="stSidebarUserContent"] [data-baseweb="select"] {{
            font-size: 0.82rem !important;
        }}

        [data-testid="stSidebarUserContent"] hr {{
            margin: 0.3rem 0 !important;
        }}

        [data-testid="stSidebarUserContent"] [data-testid="stSlider"] {{
            padding-top: 0.15rem !important;
            padding-bottom: 0.15rem !important;
        }}

        [data-testid="stSidebarUserContent"] [data-testid="stImage"] {{
            margin-bottom: 0.35rem !important;
        }}

        [data-testid="stSidebarUserContent"] [data-testid="stImage"] img {{
            object-fit: contain;
        }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
    return colors


def install_sidebar_tab_sync() -> None:
    st.html(
        """
        <div style="display:none;">
        <script>
            (function () {
                const doc = document;

                function setBlockVisibility(block, show) {
                    if (block) {
                        block.style.display = show ? "block" : "none";
                    }
                }

                function setSectionVisibility(heading, show) {
                    const section = heading.closest('[data-testid="stHeading"]')?.parentElement;
                    if (!section) return;

                    let current = section;
                    while (current) {
                        setBlockVisibility(current, show);
                        const next = current.nextElementSibling;
                        if (!next || next.querySelector('[data-testid="stHeading"] h3')) {
                            break;
                        }
                        current = next;
                    }
                }

                function syncSidebarPanels() {
                    const sidebar = doc.querySelector('[data-testid="stSidebarUserContent"]');
                    const tabs = doc.querySelectorAll('[data-testid="stTabs"] [role="tab"]');
                    if (!sidebar || !tabs[0] || !tabs[1]) return;

                    const overviewActive = tabs[0].getAttribute("aria-selected") === "true";
                    const timeSeriesActive = tabs[1].getAttribute("aria-selected") === "true";

                    sidebar.querySelectorAll("h3").forEach((heading) => {
                        const title = heading.textContent.trim();
                        if (title === "Account") {
                            setSectionVisibility(heading, true);
                        } else if (title === "Overview" || title === "Alerts") {
                            setSectionVisibility(heading, overviewActive);
                        } else if (title === "Time series" || title === "Metrics") {
                            setSectionVisibility(heading, timeSeriesActive);
                        }
                    });
                }

                function scheduleSync() {
                    syncSidebarPanels();
                    window.setTimeout(syncSidebarPanels, 50);
                }

                scheduleSync();

                const tablist = doc.querySelector('[data-testid="stTabs"]');
                if (tablist) {
                    tablist.addEventListener("click", scheduleSync);
                    new MutationObserver(scheduleSync).observe(tablist, {
                        subtree: true,
                        attributes: true,
                        attributeFilter: ["aria-selected"],
                    });
                }
            })();
        </script>
        </div>
        """,
        width="content",
        unsafe_allow_javascript=True,
    )


def configure_plotly_theme(theme: ThemeColors | None = None) -> ThemeColors:
    colors = theme or load_theme_colors()
    px.defaults.template = "plotly_white"
    px.defaults.color_discrete_sequence = chart_palette(colors)
    return colors


def style_figure(
    fig: go.Figure,
    theme: ThemeColors | None = None,
    title_color: str | None = None,
) -> go.Figure:
    colors = theme or load_theme_colors()
    fig.update_layout(
        paper_bgcolor=colors.background,
        plot_bgcolor=colors.background,
        font=dict(color=colors.text, family="Arial, sans-serif"),
        title_font=dict(color=title_color or colors.primary_dark, size=16),
        legend=dict(font=dict(color=colors.text)),
        margin=dict(l=20, r=20, t=50, b=20),
    )
    fig.update_xaxes(
        gridcolor=colors.chart.grid,
        linecolor=colors.border,
        zerolinecolor=colors.chart.grid,
    )
    fig.update_yaxes(
        gridcolor=colors.chart.grid,
        linecolor=colors.border,
        zerolinecolor=colors.chart.grid,
    )
    return fig


def series_label(region: str, brand: str, country: str) -> str:
    return f"{region} · {brand} · {country}"


def build_time_series_figure(
    plot_df: pd.DataFrame,
    metrics: list[Metric],
    title: str,
    theme: ThemeColors,
) -> go.Figure:
    metric_colors = metric_color_map(theme)
    has_count_metrics = any(metric.key != "bounce_rate" for metric in metrics)
    has_bounce_rate = any(metric.key == "bounce_rate" for metric in metrics)
    use_secondary_axis = has_bounce_rate and has_count_metrics

    fig = go.Figure()
    for metric in metrics:
        agg_fn = "sum" if metric.agg == "sum" else "mean"
        daily = (
            plot_df.groupby("dat_load", as_index=False)
            .agg(value=(metric.today, agg_fn))
            .sort_values("dat_load")
        )
        use_right_axis = metric.key == "bounce_rate" and use_secondary_axis
        fig.add_trace(
            go.Scatter(
                x=daily["dat_load"],
                y=daily["value"],
                name=metric.label,
                mode="lines",
                line=dict(color=metric_colors[metric.key], width=2),
                yaxis="y2" if use_right_axis else "y",
            )
        )

    yaxis = dict(
        title="Volume" if has_count_metrics else "Bounce rate (%)",
        gridcolor=theme.chart.grid,
        linecolor=theme.border,
        zerolinecolor=theme.chart.grid,
    )
    layout = dict(
        title=dict(text=title, font=dict(color=theme.primary_bright, size=16)),
        xaxis=dict(
            title="Date",
            gridcolor=theme.chart.grid,
            linecolor=theme.border,
            zerolinecolor=theme.chart.grid,
        ),
        yaxis=yaxis,
        height=360,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    if use_secondary_axis:
        layout["yaxis2"] = dict(
            title="Bounce rate (%)",
            overlaying="y",
            side="right",
            showgrid=False,
            linecolor=theme.border,
        )

    fig.update_layout(**layout)
    return style_figure(fig, theme, title_color=theme.primary_bright)
