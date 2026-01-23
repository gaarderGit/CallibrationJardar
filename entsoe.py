import datetime as dt
import os
import sqlite3
from pathlib import Path

import requests
import xmltodict
from dotenv import load_dotenv

load_dotenv()


security_token = os.getenv("ENTSOE_SECURITY_TOKEN")
security_params = {"securityToken": security_token}


def get(url, params, security_params):
    params.update(security_params)
    response = requests.get(url, params=params, timeout=100)
    response.raise_for_status()

    return response


def get_unit_production(area, date_from, date_to, psr_type="B12"):
    url = "https://web-api.tp.entsoe.eu/api"

    area_map = {
        "NO": "10YNO-0--------C",
        "SE": "10YSE-1--------K",
        "NO1": "10YNO-1--------2",
        "NO2": "10YNO-2--------T",
        "NO3": "10YNO-3--------J",
        "NO4": "10YNO-4--------9",
        "NO5": "10Y1001A1001A48H",
    }

    history_limit = dt.timedelta(days=180)
    if date_to - date_from > history_limit:
        date_from = date_to - history_limit

    domain = area_map[area]
    period_start = date_from
    period_end = date_to
    dt_fmt = "%Y%m%d%H%M"

    params = {
        "documentType": "A73",
        "in_Domain": domain,
        "periodStart": period_start.strftime(dt_fmt),
        "periodEnd": period_end.strftime(dt_fmt),
        "processType": "A16",
        "psrType": psr_type,
        # "RegisteredResource": "50WGI00000014365",
    }

    response = get(url, params, security_params)
    data = xmltodict.parse(response.text)

    resolution_map = {
        "PT15M": 15,
        "PT30M": 30,
        "PT60M": 60,
    }

    time_series = data["GL_MarketDocument"]["TimeSeries"]

    data_ = []
    for time_serie in time_series:
        periods = time_serie["Period"]
        if not isinstance(periods, list):
            periods = [periods]

        meta = time_serie["MktPSRType"]
        name = meta["PowerSystemResources"]["name"]
        direction = 1

        if "outBiddingZone_Domain.mRID" in time_serie:
            direction = -1

        for period in periods:
            start = dt.datetime.fromisoformat(period["timeInterval"]["start"])
            end = dt.datetime.fromisoformat(period["timeInterval"]["end"])

            resolution_str = period["resolution"]
            resolution = resolution_map[resolution_str]
            point = period["Point"]
            if not isinstance(point, list):
                point = [point]

            position_prev = 0
            quantity_prev = None
            for p in point:
                position = int(p["position"])
                quantity = float(p["quantity"]) * direction
                if int(p["position"]) - position_prev > 1:
                    # missing data points, fill with zeros
                    for missing_pos in range(position_prev + 1, position):
                        dt_ = start + dt.timedelta(
                            minutes=(missing_pos - 1) * resolution,
                        )
                        pair = (dt_, name, quantity_prev)
                        data_.append(pair)
                dt_ = start + dt.timedelta(minutes=(position - 1) * resolution)
                pair = (dt_, name, quantity)
                data_.append(pair)
                position_prev = position
                quantity_prev = quantity

            while True:
                last_dt = start + dt.timedelta(minutes=(position_prev) * resolution)
                if last_dt >= end:
                    break
                position_prev += 1
                pair = (last_dt, name, quantity_prev)
                data_.append(pair)

    return data_


def init_db(connection):
    """Creates the contacts table if it doesn't exist."""
    cursor = connection.cursor()
    create_table_query = """
    CREATE TABLE IF NOT EXISTS data (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        data_point_time TIMESTAMP NOT NULL,
        unit_name TEXT NOT NULL,
        quantity REAL NOT NULL
    );
    """
    cursor.execute(create_table_query)
    # Commit changes to the database
    connection.commit()
    print("Database table 'data' ensured.")


def add_data(connection, data_list):
    """Inserts a list of data into the database using parameterized queries."""
    cursor = connection.cursor()
    # Parameterized queries prevent SQL injection
    insert_query = (
        "INSERT INTO data (data_point_time, unit_name, quantity) VALUES (?, ?, ?)"
    )

    # Use executemany for inserting multiple rows efficiently
    cursor.executemany(insert_query, data_list)

    # Commit changes to the database
    connection.commit()
    print(f"Inserted {len(data_list)} records.")


def display_data(connection):
    """Reads and prints all data from the database."""
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM data")
    # Fetch all results
    records = cursor.fetchall()
    print("\n--- Current Contacts ---")
    for row in records:
        print(row)
    print("----------------------")


def find_latest_data_point(connection):
    """Finds and prints the latest data point time from the database."""
    cursor = connection.cursor()
    query = """
    SELECT unit_name, MAX(data_point_time) AS latest_time
    FROM data
    GROUP BY unit_name
    ORDER BY unit_name;
    """
    current_time = dt.datetime.now(tz=dt.UTC)
    current_time = current_time.replace(microsecond=0)
    cursor.execute(query)
    latest_datapoints = cursor.fetchall()
    for row in latest_datapoints:
        unit_name, latest_time = row
        print(f"{unit_name},{latest_time},{current_time}")


def insert_data(data, db_file="data.db", *, display=False):
    # Remove the file if it exists to start fresh for the sample
    if Path(db_file).exists():
        Path(db_file).unlink()
        print(f"Removed existing {db_file} to start fresh.")

    # Use a context manager to handle the connection automatically
    try:
        with sqlite3.connect(db_file) as connection:
            print(f"Connected to new database: {db_file}")

            init_db(connection)

            add_data(connection, data)
            if display:
                display_data(connection)
            find_latest_data_point(connection)

    except sqlite3.Error as e:
        print(f"A database error occurred: {e}")


if __name__ == "__main__":
    end = dt.date.today() + dt.timedelta(days=1)
    start = end - dt.timedelta(days=7 * 10)  # last 5 weeks
    area = "NO"
    types_mapped = {
        "NO": ["B12", "B10"],
        "SE": ["B12", "B14"],
    }
    print(f"Downloading production data for {area} from {start} to {end}")
    print("Downloading data overwrites existing local database.")

    prod = []
    for t in types_mapped[area]:
        prod += get_unit_production(area, start, end, psr_type=t)

    insert_data(prod, db_file="entsoe.db", display=False)
