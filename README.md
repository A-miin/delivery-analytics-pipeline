# Delivery Analytics Pipeline

A learning project: a simple ETL pipeline for delivery orders.
It creates synthetic (fake) order data, cleans it, loads it into PostgreSQL
and prepares CSV files for a Tableau dashboard.

**Stack:** Python, pandas, PostgreSQL, SQL, pytest, Tableau

## How it works

```text
generate → clean → load → export → Tableau
```

1. **Generate** – creates 1000 fake orders. Some rows are broken on purpose:
   duplicates, old versions, empty values, wrong amounts and dates.
2. **Clean** – pandas keeps the latest version of each order, fixes city names
   and removes invalid rows (1120 → 940 rows).
3. **Load** – saves orders to PostgreSQL with `INSERT ... ON CONFLICT`.
   An order is updated only if a newer version comes,
   so running the pipeline again does not create duplicates.
4. **Export** – SQL queries build reports and save them to `output/` as CSV files.

## Reports

- revenue by day
- orders by city
- average delivery time by city
- all orders (for filters in Tableau)

## How to run

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
createdb delivery_db
.venv/bin/python main.py
```

## Dashboard
https://public.tableau.com/app/profile/zulayka.isaeva/viz/DeliveryAnalyticsDashboard/Dashboard1#1

Database settings come from `PGHOST`, `PGUSER`, `PGDATABASE`
(default: `localhost`, `zulayka`, `delivery_db`).

Run tests:

```bash
.venv/bin/pytest -v
```

## What I learned

- cleaning messy data with pandas
- idempotent loading with upsert
- SQL reports with `GROUP BY` and `FILTER`
- splitting a pipeline into small steps

---

All data is fictional. Built with help from Claude Code (AI assistant).

