import os
import sqlite3

import mysql.connector
import polars as pl
from dotenv import load_dotenv

load_dotenv()


DB_PARAMS = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "port": os.getenv("DB_PORT"),
}

DB_PARAMS_LOCAL = {
    "database": "entsoe.db",
}


def execute_query(
    query: str,
    params: tuple | dict | None = None,
    *,
    strict=True,
) -> pl.DataFrame:
    """Execute a given SQL query and return the fetched rows."""
    # Create a connection

    with mysql.connector.connect(**DB_PARAMS) as conn, conn.cursor() as cursor:
        cursor.execute(query, params)
        return pl.DataFrame(
            cursor.fetchall(),
            schema=cursor.column_names,
            orient="row",
            strict=strict,
        )


def execute_query_local(
    query: str,
    params: tuple | dict | None = None,
    *,
    strict=True,
) -> pl.DataFrame:
    """Execute a given SQL query and return the fetched rows."""
    # Create a connection

    with sqlite3.connect(
        **DB_PARAMS_LOCAL,
        # detect_types=sqlite3.PARSE_DECLTYPES,
    ) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        column_names = [description[0] for description in cursor.description]
        data = cursor.fetchall()
        return pl.DataFrame(
            data,
            schema=column_names,
            orient="row",
            strict=strict,
        )


if __name__ == "__main__":
    query = "SELECT * FROM `entso-e`.actual_generation LIMIT 10;"
    rows = execute_query(query)
    for ts, val, *_ in rows:
        print(ts, val, _)
