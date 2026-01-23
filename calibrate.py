# ruff: noqa: N806  # Variable in function should be lowercase

import argparse
import datetime as dt
import textwrap
from pprint import pprint

import numpy as np
import polars as pl
import scipy.optimize as opt

from db import execute_query, execute_query_local

config = {
    "Kvilldal": {
        "indirect_process_object_id": 359,
        "entso_e_unit_names": [
            "KVILLDALG1      HYDRO",
            "KVILLDALG2      HYDRO",
            "KVILLDALG3      HYDRO",
            "KVILLDALG4      HYDRO",
            # "Kvilldalg1 Hydro",
            # "Kvilldalg2 Hydro",
            # "Kvilldalg3 Hydro",
            # "Kvilldalg4 Hydro",
        ],
    },
    "Saurdal": {
        "indirect_process_object_id": 340,
        "entso_e_unit_names": [
            "SAURDAL G1      HYDRO",
            "SAURDAL G2      HYDRO",
            "Saurdal G3 Hydro",
            "Saurdal G4 Hydro",
            # "Saurdal G1 Hydro",
            # "Saurdal G2 Hydro",
            # "Saurdal G3 Hydro",
            # "Saurdal G4 Hydro",
        ],
    },
    "Sima": {
        "indirect_process_object_id": 50,
        "entso_e_unit_names": [
            "SIMA    G1      HYDRO",
            "SIMA    G2      HYDRO",
            "SIMA    G3      HYDRO",
            "SIMA    G4      HYDRO",
        ],
    },
    "Aurland3": {
        "indirect_process_object_id": 337,
        "entso_e_unit_names": [
            "AURLAND3G1      HYDRO",
            "AURLAND3G2      HYDRO",
        ],
    },
}


def get_production_object_ids_from_indirect(indirect_process_object_id: int):
    query = """
    SELECT *
    FROM ably_field_data.indirect_process_object_relations
    WHERE indirect_process_object_id = %(indirect_process_object_id)s;
    """

    params = {"indirect_process_object_id": indirect_process_object_id}
    return execute_query(query, params=params)


def get_measurement_for_process_object(
    process_object_id: int,
    from_ts: str | None = None,
    to_ts: str | None = None,
):
    if to_ts is None:
        to_ts = dt.datetime.now(dt.UTC).strftime("%Y-%m-%d %H:%M:%S")
    if from_ts is None:
        from_ts = (dt.datetime.now(dt.UTC) - dt.timedelta(days=7)).strftime(
            "%Y-%m-%d %H:%M:%S",
        )
    query = """
    SELECT *
    FROM ably_field_data.line_measurement
    WHERE process_object_id = %(process_object_id)s
    AND realtime >= %(from_ts)s
    AND realtime <= %(to_ts)s
    ORDER BY realtime DESC;
    """

    params = {
        "process_object_id": process_object_id,
        "from_ts": from_ts,
        "to_ts": to_ts,
    }
    return execute_query(query, params=params)


def get_entso_e_generation_data(unit_names: list[str], from_ts: str, to_ts: str):
    query = f"""
    SELECT *
    FROM `entso-e`.actual_generation
    WHERE unit_name IN ({", ".join(["%s"] * len(unit_names))})
    AND `data_point_time` >= %s
    AND `data_point_time` <= %s
    AND resolution = 'PT15M'
    ORDER BY `data_point_time` DESC;
    """
    params = [*unit_names, from_ts, to_ts]
    return execute_query(query, params=params)


def get_entso_e_generation_data_local(unit_names: list[str], from_ts: str, to_ts: str):
    query = f"""
    SELECT *
    FROM data
    WHERE unit_name IN ({", ".join(["?"] * len(unit_names))})
    AND `data_point_time` >= ?
    AND `data_point_time` <= ?
    ORDER BY `data_point_time` DESC;
    """
    params = [*unit_names, from_ts, to_ts]
    return execute_query_local(query, params=params)


def get_magnetic_ms_ids_from_process_object_ids(ids):
    query = f"""
    SELECT mp.*,
    ml.id AS ml_id,
    ml.measure_site_id,
    ml.land_owner_id,
    ml.magnetic_ms_id,
    ml.m_ms_x_point,
    ml.m_ms_y_point,
    ml.m_ms_z_point,
    ml.m_ms_perpendicular_rotation,
    ml.m_ms_parallel_rotation,
    ml.m_ms_heading,
    ml.m_ms_longitude,
    ml.m_ms_latitude,
    ml.m_ms_altitude,
    ml.mount_type,
    ml.mount_comment,
    ml.m_ms_location_number,
    ml.xy_deg_change_limit,
    ml.change_comment AS ml_change_comment
    FROM ably_field_data.measurement_and_process_object_relations AS mp
    INNER JOIN ably_field_data.magnetic_ms_locations AS ml
    ON mp.magnetic_ms_location_id = ml.id
    WHERE mp.process_objects_id IN ({", ".join(["%s"] * len(ids))});
    """
    params = ids
    return execute_query(query, params=params)


def get_magnetic_ms_measurements(ids, from_ts, to_ts):
    query = f"""
    SELECT *
    FROM ably_historic_data.raw_magnetic_ms
    WHERE magnetic_ms_id IN ({", ".join(["%s"] * len(ids))})
    AND realtime >= %s
    AND realtime <= %s
    ORDER BY realtime DESC;
    """
    params = [*ids, from_ts, to_ts]
    return execute_query(query, params=params, strict=False)


def get_magnetic_ms_measurements_from_indirect_id(id_, from_ts, to_ts):
    objects = get_production_object_ids_from_indirect(id_)
    ms_ids = get_magnetic_ms_ids_from_process_object_ids(
        objects["direct_process_object_id"].to_list(),
    )

    return get_magnetic_ms_measurements(
        ms_ids["magnetic_ms_id"].to_list(),
        from_ts,
        to_ts,
    )


def test_query():
    query = """
    SELECT *
    FROM `entso-e`.actual_generation
    LIMIT 10;
    """

    rows = execute_query(query)

    print(rows)


def get_line_measurements(ids, from_ts, to_ts):
    query = f"""
    SELECT *
    FROM ably_field_data.line_measurement
    WHERE process_object_id IN ({", ".join(["%s"] * len(ids))})
    AND realtime >= %s
    AND realtime <= %s
    ORDER BY realtime DESC;
    """
    params = [*ids, from_ts, to_ts]
    return execute_query(query, params=params)


def get_line_measurements_from_indirect(
    indirect_process_object_id: int,
    from_ts: str,
    to_ts: str,
):
    objects = get_production_object_ids_from_indirect(indirect_process_object_id)

    return get_line_measurements(
        objects["direct_process_object_id"].to_list(),
        from_ts,
        to_ts,
    )


def get_gainset_ids_from_magnetic_ms_ids(ids):
    query = f"""
    SELECT
    mag.id,
    mag.current_magnetic_ms_setting_id,
    settings.magnetic_ms_monitor_calibration_id,
    settings.magnetic_ms_signal_calibration_id,
    calibrations.gainset_id,
    calibrations.status,
    calibrations.call_mms_v_x,
    calibrations.call_mms_v_y,
    calibrations.call_mms_m_x,
    calibrations.call_mms_m_y
    FROM ably_field_data.magnetic_ms AS mag
    JOIN ably_field_data.magnetic_ms_settings AS settings
    ON mag.current_magnetic_ms_setting_id = settings.id
    JOIN ably_field_data.magnetic_ms_signal_calibrations AS calibrations
    ON settings.magnetic_ms_signal_calibration_id = calibrations.id
    WHERE mag.id IN ({", ".join(["%s"] * len(ids))})
    ORDER BY mag.id;
    """

    params = ids
    return execute_query(query, params=params, strict=False)


def get_gainset_from_indirect(
    indirect_process_object_id: int,
):
    objects = get_production_object_ids_from_indirect(indirect_process_object_id)

    ms_ids = get_magnetic_ms_ids_from_process_object_ids(
        objects["direct_process_object_id"].to_list(),
    )

    return get_gainset(ms_ids["magnetic_ms_id"].to_list())


def get_gainset(ids):
    query = f"""
    SELECT *
    FROM ably_field_data.gains
    WHERE gainset_id IN ({", ".join(["%s"] * len(ids))});
    """

    params = ids
    return execute_query(query, params=params, strict=False)


def get_tt_ms(ids, from_ts, to_ts):
    query = f"""
    SELECT *
    FROM ably_historic_data.raw_tt_ms
    WHERE tt_ms_id IN ({", ".join(["%s"] * len(ids))})
    AND realtime >= %s
    AND realtime <= %s
    ORDER BY realtime DESC;
    """
    params = [*ids, from_ts, to_ts]
    return execute_query(query, params=params)


def get_object_relations():
    query = """
    SELECT * FROM ably_field_data.indirect_process_object_relations;
    """

    return execute_query(query)


def get_all_related_objects(
    indirect_process_object_id: int,
    prev_ids=None,
    objects=None,
):
    if prev_ids is None:
        prev_ids = set()

    prev_ids |= {indirect_process_object_id}
    print(indirect_process_object_id)
    relations = objects.filter(
        pl.col("indirect_process_object_id") == indirect_process_object_id,
    )

    rel = objects.filter(
        pl.col("direct_process_object_id").is_in(relations["direct_process_object_id"]),
    )

    indirect_process_object_ids = set(rel["indirect_process_object_id"].unique())

    # print(indirect_process_object_ids)

    objs = set()

    for obj_id in indirect_process_object_ids - prev_ids:
        objs |= get_all_related_objects(obj_id, prev_ids, objects)

    objs |= indirect_process_object_ids
    return objs


def fit_calibration_linear(df: pl.DataFrame, y_var: str, x_vars: list[str]):
    y = df[y_var].to_numpy()
    X = df[x_vars].to_numpy()
    column_names = x_vars

    b, *_ = np.linalg.lstsq(X, y, rcond=None)

    y_hat = X @ b

    params_id = [int(x) for x in column_names]

    param_df = pl.DataFrame(
        {
            "direct_process_object_id": params_id,
            "b": b,
        },
    )

    fit_df = pl.DataFrame(
        {
            "fit": y_hat,
            "data_point_time": df["data_point_time"],
        },
    )

    return fit_df, param_df


def fit_calibration(df):
    print("Fitting calibration...")

    X_full = df.to_numpy()
    column_names = df.columns

    print(column_names)
    X_names = column_names[1:-1]
    n_vars = int(len(X_names) / 2)
    X_names = X_names[:n_vars]
    X = X_full[:, 1 : n_vars + 1]  # Features: line raw value
    y = X_full[:, -1]  # Target: entso generation

    print(X)
    print(y)

    b, res, rank, s = np.linalg.lstsq(X, y, rcond=None)

    meta = {"res": res, "rank": rank, "s": s}

    y_hat = X @ b

    pprint(b)
    pprint(list(zip(X_names, b, strict=False)))
    pprint(meta)

    params_id = [int(x.split("_")[-1]) for x in X_names]

    pprint(params_id)

    param_df = pl.DataFrame(
        {
            "direct_process_object_id": params_id,
            "b": b,
        },
    )

    pprint(y_hat)

    print("Done fitting calibration.")

    fit_df = pl.DataFrame(
        {
            "predicted": y_hat,
            "realtime": df["realtime"],
        },
    )

    return fit_df, param_df


def calc_power(b, power, power_factor_tan):
    shape = np.shape(power)
    n_vars = shape[1]
    b_power = b[:n_vars]
    b_phase = b[n_vars:]

    phase_adjustment = np.cos(b_phase) - power_factor_tan * np.sin(b_phase)
    return (power * phase_adjustment) @ b_power


def objective(b, power, power_factor, y):
    y_hat = calc_power(b, power, power_factor)
    return np.sqrt(np.mean(np.square(y_hat - y)))


def fit_calibration2(df):
    print("Fitting calibration...")

    X_full = df.to_numpy()
    X_main = X_full[:, 1:-1]
    y = X_full[:, -1]
    column_names = df.columns

    X_names = column_names[1:-1]

    n_vars = int(len(X_names) / 2)

    power = X_main[:, :n_vars]
    power_factor = X_main[:, n_vars:]

    b0 = np.array([1.0] * n_vars + [0.0] * n_vars)

    objective(b0, power, np.tan(power_factor), y)
    res = opt.minimize(
        objective,
        b0,
        args=(power, np.tan(power_factor), y),
        method="Nelder-Mead",
    )
    print(res)
    b = res.x

    y_hat = calc_power(b, power, np.tan(power_factor))

    params_id = [int(x.split("_")[-1]) for x in X_names][:n_vars]

    param_df = pl.DataFrame(
        {
            "direct_process_object_id": params_id,
            "b": b[:n_vars],
            "phase_adjustment": b[n_vars:],
        },
    )

    pprint(y_hat)

    print("Done fitting calibration.")

    fit_df = pl.DataFrame(
        {
            "predicted": y_hat,
            "realtime": df["realtime"],
        },
    )

    return fit_df, param_df


def calibrate(config, ts_from, ts_to):
    entso_df_raw = get_entso_e_generation_data_local(
        config["entso_e_unit_names"],
        ts_from,
        ts_to,
    ).with_columns(
        pl.col("data_point_time").str.to_datetime(format="%Y-%m-%d %H:%M:%S%z"),
        pl.col("quantity") * 1000,  # Convert to kW
    )

    print(entso_df_raw)

    entso_df = (
        entso_df_raw.pivot(
            index="data_point_time",
            on="unit_name",
            values="quantity",
            aggregate_function="first",
        )
        .drop_nulls()
        .unpivot(
            index="data_point_time",
            variable_name="unit_name",
            value_name="quantity",
        )
        .group_by("data_point_time")
        .agg(pl.col("quantity").sum().alias("entso_generation"))
        .sort("data_point_time")
    ).with_columns(pl.col("entso_generation").cast(pl.Float64))

    resolution = entso_df["data_point_time"].diff().mode().first().total_seconds() / 60
    resolution = int(resolution)
    entso_df = entso_df.upsample("data_point_time", every="1m", maintain_order=True)
    entso_df = entso_df.fill_null(strategy="forward", limit=resolution - 1)

    print(entso_df)

    line_df_raw = get_line_measurements_from_indirect(
        config["indirect_process_object_id"],
        ts_from,
        ts_to,
    ).with_columns(
        pl.col("realtime").dt.replace_time_zone("UTC"),
    )

    line_df = (
        line_df_raw.pivot(
            index="realtime",
            on="process_object_id",
            values="value",
            aggregate_function="first",
        )
        .drop_nulls()
        .sort("realtime")
    )

    joined_df = entso_df.join(
        line_df,
        left_on="data_point_time",
        right_on="realtime",
        how="inner",
    ).drop_nulls()

    print(joined_df)

    y_var = "entso_generation"
    x_vars = [col for col in joined_df.columns if col not in ("data_point_time", y_var)]
    return fit_calibration_linear(joined_df, y_var, x_vars)


def generate_sql_update(
    params_df: pl.DataFrame,
    indirect_process_object_id: int,
) -> str:
    sql = "START TRANSACTION;\n"

    for row in sorted(params_df.iter_rows(), key=lambda x: x[0]):
        direct_process_object_id, b = row
        sql += textwrap.dedent(
            f"""
            UPDATE ably_field_data.indirect_process_object_relations
            SET primary_calibration_factor = {b:.3f}
            WHERE direct_process_object_id = {direct_process_object_id}
            AND indirect_process_object_id = {indirect_process_object_id};
            """,
        )

    sql += "\n"
    sql += "COMMIT;\n"

    return sql


def print_sql(params_df: pl.DataFrame, indirect_process_object_id: int):
    print(generate_sql_update(params_df, indirect_process_object_id))


def main():
    parser = argparse.ArgumentParser(
        description="Run ENTSO-E calibration for a given area and time range",
    )

    parser.add_argument(
        "--area",
        required=True,
        help="Input area name (e.g. Saurdal)",
    )

    parser.add_argument(
        "--from",
        dest="ts_from",
        required=True,
        type=dt.datetime.fromisoformat,
        help="Start datetime (ISO format, UTC)",
    )

    parser.add_argument(
        "--to",
        dest="ts_to",
        required=True,
        type=dt.datetime.fromisoformat,
        help="End datetime (ISO format, UTC)",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        default=False,
        help="Print intermediate dataframes",
    )

    args = parser.parse_args()

    cfg = config[args.area]

    fit_df, params_df = calibrate(
        config=cfg,
        ts_from=args.ts_from,
        ts_to=args.ts_to,
    )

    if args.verbose:
        print("#############")
        print(fit_df)
        print(params_df)

    print_sql(params_df, indirect_process_object_id=cfg["indirect_process_object_id"])


if __name__ == "__main__":
    main()
