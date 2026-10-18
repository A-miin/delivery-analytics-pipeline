"""Step 1: generate synthetic delivery orders, including deliberately dirty records.

All orders and customers are fictional. Only city names are real,
so Tableau can show them on a map.
"""

import logging
import random
from datetime import timedelta

import pandas as pd

from src import config

logger = logging.getLogger(__name__)

# City -> (share of all orders, typical delivery time in minutes).
CITIES = {
    "Bishkek": (0.30, 35),
    "Almaty": (0.25, 40),
    "Tashkent": (0.20, 45),
    "Osh": (0.10, 30),
    "Astana": (0.10, 38),
    "Samarkand": (0.05, 28),
}
NUM_CUSTOMERS = 300
CANCEL_RATE = 0.12
MIN_AMOUNT = 300
MAX_AMOUNT = 5000

# How many orders get each kind of problem. The groups do not overlap,
# so the numbers in the cleaning report can be checked against this table.
DIRTY_COUNTS = {
    "old_version": 80,  # an extra, older row of the same order
    "exact_duplicate": 30,  # the same row twice
    "conflicting_duplicate": 10,  # same order_id and updated_at, different amount
    "missing_city": 30,
    "messy_city": 100,  # extra spaces, wrong letter case
    "missing_amount": 20,
    "non_positive_amount": 20,
    "delivered_before_created": 20,
}


def make_order(rng: random.Random, number: int) -> dict:
    """Create one clean order. `number` becomes part of the order_id."""
    city = rng.choices(list(CITIES), weights=[share for share, _ in CITIES.values()])[0]

    # Orders are placed between 08:00 and 23:00 on a random day of the period.
    created_at = config.PERIOD_START + timedelta(
        days=rng.randrange(config.PERIOD_DAYS),
        minutes=rng.randint(8 * 60, 23 * 60),
    )

    if rng.random() < CANCEL_RATE:
        status = "cancelled"
        delivered_at = None
        updated_at = created_at + timedelta(minutes=rng.randint(5, 30))
    else:
        status = "delivered"
        typical_minutes = CITIES[city][1]
        # Delivery time varies around the city's typical value, but is never below 10 minutes.
        delivery_minutes = max(10, round(rng.gauss(typical_minutes, 8)))
        delivered_at = created_at + timedelta(minutes=delivery_minutes)
        updated_at = delivered_at

    return {
        "order_id": f"ORD-{number:05d}",
        "customer_id": f"CUST-{rng.randint(1, NUM_CUSTOMERS):04d}",
        "city": city,
        "status": status,
        "amount": round(rng.uniform(MIN_AMOUNT, MAX_AMOUNT), 2),
        "created_at": created_at,
        "delivered_at": delivered_at,
        "updated_at": updated_at,
    }


def add_dirty_records(rng: random.Random, orders: list[dict]) -> list[dict]:
    """Spoil some orders in place and return extra rows (duplicates and old versions)."""
    # Orders are taken from a shuffled pool and removed from it,
    # so every order gets at most one problem.
    pool = list(range(len(orders)))
    rng.shuffle(pool)

    def take(count: int, only_delivered: bool = False) -> list[dict]:
        picked = [i for i in pool if not only_delivered or orders[i]["status"] == "delivered"]
        picked = picked[:count]
        for i in picked:
            pool.remove(i)
        return [orders[i] for i in picked]

    extra_rows = []

    for order in take(DIRTY_COUNTS["old_version"]):
        # The first version of the order: just created, not delivered yet.
        extra_rows.append(
            dict(order, status="created", delivered_at=None, updated_at=order["created_at"])
        )

    for order in take(DIRTY_COUNTS["exact_duplicate"]):
        extra_rows.append(dict(order))

    for order in take(DIRTY_COUNTS["conflicting_duplicate"]):
        new_amount = round(order["amount"] + rng.choice([-100, 100]), 2)
        extra_rows.append(dict(order, amount=new_amount))

    for order in take(DIRTY_COUNTS["missing_city"]):
        order["city"] = None

    for order in take(DIRTY_COUNTS["messy_city"]):
        city = order["city"]
        order["city"] = rng.choice([f"  {city.lower()} ", city.upper(), f"{city}   "])

    for order in take(DIRTY_COUNTS["missing_amount"]):
        order["amount"] = None

    for order in take(DIRTY_COUNTS["non_positive_amount"]):
        order["amount"] = rng.choice([0, -order["amount"]])

    for order in take(DIRTY_COUNTS["delivered_before_created"], only_delivered=True):
        order["delivered_at"] = order["created_at"] - timedelta(minutes=rng.randint(5, 60))

    return extra_rows


def generate_orders(
    seed: int = config.RANDOM_SEED, num_orders: int = config.NUM_ORDERS
) -> pd.DataFrame:
    """Return raw orders: clean orders plus dirty records, in random order."""
    rng = random.Random(seed)
    orders = [make_order(rng, number) for number in range(1, num_orders + 1)]
    rows = orders + add_dirty_records(rng, orders)
    # Real source files are not sorted, so we shuffle the rows too.
    rng.shuffle(rows)
    return pd.DataFrame(rows, columns=config.ORDER_COLUMNS)


def run() -> pd.DataFrame:
    """Generate raw orders and save them to data/raw/orders.csv."""
    orders = generate_orders()

    config.RAW_ORDERS_PATH.parent.mkdir(parents=True, exist_ok=True)
    orders.to_csv(config.RAW_ORDERS_PATH, index=False, float_format="%.2f")

    logger.info(
        "Generated %d unique orders, %d rows in total",
        orders["order_id"].nunique(),
        len(orders),
    )
    logger.info("Dirty records added: %s", DIRTY_COUNTS)
    logger.info("Saved raw orders to %s", config.RAW_ORDERS_PATH.relative_to(config.PROJECT_ROOT))
    return orders


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format=config.LOG_FORMAT)
    run()
