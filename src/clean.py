"""Step 2: clean raw orders with pandas.

Rules:
- several versions of one order -> keep the one with the latest updated_at;
  if updated_at is the same, the row that comes later in the file wins;
- city: trim spaces, fix letter case, empty city -> "Unknown";
- missing amount, amount <= 0, delivered_at before created_at -> remove the row.
"""

import logging

import pandas as pd

from src import config

logger = logging.getLogger(__name__)

UNKNOWN_CITY = "Unknown"

# Rows we cannot fix. Each rule returns True for the rows to remove.
# Comparisons with a missing value (NaN / NaT) return False,
# so each rule catches only its own problem.
INVALID_ROW_RULES = {
    "missing amount": lambda orders: orders["amount"].isna(),
    "amount <= 0": lambda orders: orders["amount"] <= 0,
    "delivered before created": lambda orders: orders["delivered_at"] < orders["created_at"],
}


def read_raw_orders(path=config.RAW_ORDERS_PATH) -> pd.DataFrame:
    return pd.read_csv(path, parse_dates=config.DATETIME_COLUMNS)


def keep_latest_version(orders: pd.DataFrame) -> pd.DataFrame:
    """Keep one row per order_id: the one with the latest updated_at.

    A stable sort keeps the original file order for rows with the same
    updated_at. So after sorting, the last row of each order_id is the
    latest version, and for a tie it is the row that came later in the file.
    Rows without updated_at go first, so they are treated as the oldest.
    """
    ordered = orders.sort_values("updated_at", kind="stable", na_position="first")
    return ordered.drop_duplicates(subset="order_id", keep="last")


def normalize_cities(orders: pd.DataFrame) -> pd.DataFrame:
    """'  bishkek ' -> 'Bishkek', 'ALMATY' -> 'Almaty', empty city -> 'Unknown'."""
    city = orders["city"].fillna("").str.strip().str.title()
    return orders.assign(city=city.replace("", UNKNOWN_CITY))


def remove_invalid_rows(orders: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """Apply INVALID_ROW_RULES one by one and count removed rows for each rule."""
    removed = {}
    for reason, is_invalid in INVALID_ROW_RULES.items():
        mask = is_invalid(orders)
        removed[f"removed: {reason}"] = int(mask.sum())
        orders = orders[~mask]
    return orders, removed


def clean_orders(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, int]]:
    """Apply all cleaning rules. Return clean orders and a report with row counts."""
    report = {"rows in": len(raw)}

    # Pick the latest version first and validate it after that. If the latest
    # version is broken, we drop the order instead of silently falling back
    # to an older version with outdated data.
    orders = keep_latest_version(raw)
    report["removed: duplicates and old versions"] = len(raw) - len(orders)

    orders = normalize_cities(orders)
    report["fixed: empty city -> Unknown"] = int((orders["city"] == UNKNOWN_CITY).sum())

    orders, removed = remove_invalid_rows(orders)
    report.update(removed)

    orders = orders.sort_values("order_id").reset_index(drop=True)
    report["rows out"] = len(orders)
    return orders, report


def run() -> pd.DataFrame:
    """Read data/raw/orders.csv, clean it and save to data/processed/orders.csv."""
    raw = read_raw_orders()
    orders, report = clean_orders(raw)

    config.PROCESSED_ORDERS_PATH.parent.mkdir(parents=True, exist_ok=True)
    orders.to_csv(
        config.PROCESSED_ORDERS_PATH,
        index=False,
        float_format="%.2f",
        date_format="%Y-%m-%d %H:%M:%S",
    )

    report_lines = "\n".join(f"  {name}: {count}" for name, count in report.items())
    logger.info("Cleaning report:\n%s", report_lines)
    logger.info(
        "Saved clean orders to %s",
        config.PROCESSED_ORDERS_PATH.relative_to(config.PROJECT_ROOT),
    )
    return orders


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format=config.LOG_FORMAT)
    run()
