""" run analytics sql queries and export to csv for Tableau
    every .sql file became with same name: revenue.sql->revenue.csv
"""
import logging
from pathlib import Path

import pandas as pd
import psycopg

from src import config

logger = logging.getLogger(__name__)

def run_query(conn: psycopg.Connection, sql: str)->pd.DataFrame:
    """run select and get result as dataframe"""
    cursor = conn.execute(sql)
    columns = [column.name for column in cursor.description]
    return pd.DataFrame(cursor.fetchall(), columns=columns)

def export_query(conn: psycopg.Connection, sql_path: Path)->Path:
    """run sql file and save the result to output/...csv"""
    result = run_query(conn, sql_path.read_text(encoding="utf-8"))
    csv_path = config.OUTPUT_DIR / f"{sql_path.stem}.csv"
    result.to_csv(csv_path, index=False)

    logger.info("exported %d rows to %s", len(result), csv_path.relative_to(config.PROJECT_ROOT))
    return csv_path

def run() -> list[Path]:
    """export queries from sql/analytics to output/"""
    config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    sql_files = sorted(config.ANALYTICS_SQL_DIR.glob("*.sql"))
    with psycopg.connect(**config.DB_SETTINGS) as conn:
        return [export_query(conn, sql_path) for sql_path in sql_files]


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format=config.LOG_FORMAT)
    run()
