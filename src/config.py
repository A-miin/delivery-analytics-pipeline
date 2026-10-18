"""Project settings in one place: file paths and data generation parameters."""

from datetime import datetime
from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_ORDERS_PATH = PROJECT_ROOT / "data" / "raw" / "orders.csv"
PROCESSED_ORDERS_PATH = PROJECT_ROOT / "data" / "processed" / "orders.csv"
SCHEMA_SQL_PATH = PROJECT_ROOT /"sql"/"schema.sql"
UPSERT_SQL_PATH = PROJECT_ROOT /"sql"/"upsert_orders.sql"

ANALYTICS_SQL_DIR = PROJECT_ROOT/"sql"/"analytics"
OUTPUT_DIR = PROJECT_ROOT/"output"

# Fixed seed and fixed period: every run produces exactly the same data.
RANDOM_SEED = 42
NUM_ORDERS = 1000
PERIOD_START = datetime(2026, 9, 1)
PERIOD_DAYS = 30

# Columns of the orders data, in the order they are written to CSV.
ORDER_COLUMNS = [
    "order_id",
    "customer_id",
    "city",
    "status",
    "amount",
    "created_at",
    "delivered_at",
    "updated_at",
]
DATETIME_COLUMNS = ["created_at", "delivered_at", "updated_at"]

LOG_FORMAT = "%(asctime)s %(levelname)s %(name)s: %(message)s"

# Database connection. Standard PostgreSQL variables (PGHOST, PGUSER, PGDATABASE)
# override these defaults, so the code works on another machine without changes.
DB_SETTINGS = {
    "host": os.environ.get("PGHOST", "localhost"),
    "user": os.environ.get("PGUSER", "zulayka"),
    "dbname": os.environ.get("PGDATABASE", "delivery_db"),
}
