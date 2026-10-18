"""Tests for the cleaning step (src/clean.py)."""

import pandas as pd

from src.clean import clean_orders


def make_row(**changes) -> dict:
    """Return a valid delivered order. Keyword arguments replace its fields."""
    row = {
        "order_id": "ORD-00001",
        "customer_id": "CUST-0001",
        "city": "Bishkek",
        "status": "delivered",
        "amount": 1000.0,
        "created_at": pd.Timestamp("2026-09-01 12:00"),
        "delivered_at": pd.Timestamp("2026-09-01 12:40"),
        "updated_at": pd.Timestamp("2026-09-01 12:40"),
    }
    row.update(changes)
    return row


def test_keeps_latest_version_of_order():
    raw = pd.DataFrame(
        [
            make_row(status="delivered", updated_at=pd.Timestamp("2026-09-01 12:40")),
            # The older version comes later in the file, but must still lose.
            make_row(
                status="created",
                delivered_at=None,
                updated_at=pd.Timestamp("2026-09-01 12:00"),
            ),
        ]
    )

    clean, _ = clean_orders(raw)

    assert len(clean) == 1
    assert clean.loc[0, "status"] == "delivered"


def test_same_updated_at_keeps_row_that_comes_later_in_file():
    raw = pd.DataFrame([make_row(amount=1000.0), make_row(amount=1100.0)])

    clean, _ = clean_orders(raw)

    assert clean["amount"].tolist() == [1100.0]


def test_removes_invalid_rows_and_counts_them():
    raw = pd.DataFrame(
        [
            make_row(order_id="ORD-00001"),
            make_row(order_id="ORD-00002", amount=None),
            make_row(order_id="ORD-00003", amount=0.0),
            make_row(order_id="ORD-00004", amount=-50.0),
            make_row(order_id="ORD-00005", delivered_at=pd.Timestamp("2026-09-01 11:00")),
        ]
    )

    clean, report = clean_orders(raw)

    assert clean["order_id"].tolist() == ["ORD-00001"]
    assert report["removed: missing amount"] == 1
    assert report["removed: amount <= 0"] == 2
    assert report["removed: delivered before created"] == 1
