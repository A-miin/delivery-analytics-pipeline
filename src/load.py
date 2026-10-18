"""Step 3: load clean orders into PostgreSQL.

The orders table is created if needed (sql/schema.sql). Every order is
upserted (sql/upsert_orders.sql): new orders are inserted, existing ones
are updated only when the incoming updated_at is strictly newer.
"""
import logging
import pandas as pd
import psycopg

from src import config

logger = logging.getLogger(__name__)

def read_clean_orders(path=config.PROCESSED_ORDERS_PATH) -> list[dict]:
    """Read clean orders as a list of dicts: one dict per order."""
    orders = pd.read_csv(path, parse_dates=config.DATETIME_COLUMNS)
    # pandas marks empty values as NaN / NaT, the database expects None (NULL).
    orders = orders.astype(object).where(orders.notna(), None)
    return orders.to_dict(orient="records")


def count_orders(conn: psycopg.Connection) -> int:
    return conn.execute("SELECT count(*) FROM orders").fetchone()[0]


def load_orders(orders: list[dict]) -> dict[str, int]:
    """Create the table if needed, upsert all orders and return row counts."""
    schema_sql = config.SCHEMA_SQL_PATH.read_text(encoding="utf-8")
    upsert_sql = config.UPSERT_SQL_PATH.read_text(encoding="utf-8")

    # One connection block = one transaction: if anything fails, nothing is saved.
    with psycopg.connect(**config.DB_SETTINGS) as conn:
        conn.execute(schema_sql)
        rows_before = count_orders(conn)

        with conn.cursor() as cursor:
            cursor.executemany(upsert_sql, orders)
            changed = cursor.rowcount  # inserted + updated rows

        inserted = count_orders(conn) - rows_before

    return {
        "orders in file": len(orders),
        "inserted": inserted,
        "updated": changed - inserted,
        "unchanged": len(orders) - changed,
    }


def run() -> dict[str, int]:
    """Read data/processed/orders.csv and load it into the orders table."""
    report = load_orders(read_clean_orders())

    report_lines = "\n".join(f"  {name}: {count}" for name, count in report.items())
    logger.info("Load report:\n%s", report_lines)
    return report


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format=config.LOG_FORMAT)
    run()