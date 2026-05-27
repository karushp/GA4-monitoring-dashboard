from pathlib import Path

APP_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = APP_ROOT / "data"
SIDEBAR_LOGO = APP_ROOT / "img" / "Union.jpg"

ALERT_GREEN = "#bed986"
ALERT_RED = "#e8707a"
TABLE_HEIGHT = "content"
TIME_SERIES_LOOKBACK_DAYS = 90
TIME_SERIES_CHARTS_PER_PAGE = 10

PAGE_TITLE = "Data Monitor Dashboard"
PAGE_ICON = "📊"
