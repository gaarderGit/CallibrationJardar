import datetime as dt

import plotly.graph_objects as go
import polars as pl
from dash import Dash, Input, Output, dcc, html

from calibrate import (
    config,
    fit_calibration_linear,
    generate_sql_update,
    get_entso_e_generation_data_local,
    get_line_measurements_from_indirect,
    get_production_object_ids_from_indirect,
)

app = Dash(__name__)

app.layout = html.Div(
    style={"padding": "20px"},
    children=[
        html.H2("ENTSO-E vs Line Measurements"),
        html.Div(
            [
                html.Div(
                    [
                        html.Div(
                            [
                                html.Label("Select plant"),
                                dcc.Dropdown(
                                    id="config-select",
                                    options=[
                                        {"label": k, "value": k} for k in config
                                    ],
                                    value="Kvilldal",
                                    clearable=False,
                                ),
                            ],
                            style={"width": "200px"},
                        ),
                        html.Br(),
                        html.Div(
                            [
                                html.Label("Date range"),
                                dcc.DatePickerRange(
                                    id="date-range",
                                    start_date=dt.date.today() - dt.timedelta(days=35),
                                    end_date=dt.date.today(),
                                    display_format="YYYY-MM-DD",
                                ),
                            ],
                            style={"width": "200px"},
                        ),
                    ],
                ),
                html.Div(
                    [
                        html.H4("Calibration factors"),
                        dcc.Loading(
                            html.Div(id="calibration-table"),
                            type="default",
                        ),
                    ],
                ),
                html.Div(
                    [
                        html.H4("Error metrics"),
                        dcc.Loading(
                            html.Div(id="error-table"),
                            type="default",
                        ),
                    ],
                ),
                html.Div(
                    [
                        html.H4("SQL"),
                        dcc.Loading(
                            html.Pre(id="sql-output"),
                            type="default",
                        ),
                    ],
                ),
            ],
            style={"display": "flex", "gap": "20px", "alignItems": "top"},
        ),
        html.Br(),
        dcc.Loading(
            dcc.Graph(id="timeseries-plot"),
            type="default",
        ),
        html.Hr(),
        html.H4("Underlying ENTSO-E curves"),
        dcc.Loading(
            dcc.Graph(id="entso-raw-plot"),
            type="default",
        ),
        html.Hr(),
        html.H4("Underlying line measurements"),
        dcc.Loading(
            dcc.Graph(id="line-raw-plot"),
            type="default",
        ),
        html.Hr(),
        html.H4("Underlying line measurements phase"),
        dcc.Loading(
            dcc.Graph(id="line-raw-phase-plot"),
            type="default",
        ),
        html.Hr(),
        html.H4("Underlying power factors"),
        dcc.Loading(
            dcc.Graph(id="line-raw-pf-plot"),
            type="default",
        ),
    ],
)


@app.callback(
    Output("timeseries-plot", "figure"),
    Output("entso-raw-plot", "figure"),
    Output("line-raw-plot", "figure"),
    Output("line-raw-phase-plot", "figure"),
    Output("line-raw-pf-plot", "figure"),
    Output("calibration-table", "children"),
    Output("error-table", "children"),
    Output("sql-output", "children"),
    Input("config-select", "value"),
    Input("date-range", "start_date"),
    Input("date-range", "end_date"),
)
def update_plot(config_name, start_date, end_date):
    from_ts = f"{start_date} 00:00:00"
    to_ts = f"{end_date} 23:59:59"

    cfg = config[config_name]

    # --- ENTSO-E data ---
    conversion_factor_mw_to_kw = 1000
    entso_df_raw = get_entso_e_generation_data_local(
        cfg["entso_e_unit_names"],
        from_ts,
        to_ts,
    ).with_columns(
        pl.col("data_point_time").str.to_datetime(format="%Y-%m-%d %H:%M:%S%z"),
        pl.col("quantity").cast(pl.Float64) * conversion_factor_mw_to_kw,
    )

    entso_df_filtered = (
        entso_df_raw.with_columns(pl.col("data_point_time").cast(pl.Datetime))
        .pivot(
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
        .sort("data_point_time")
    )

    entso_df = (
        entso_df_filtered.with_columns(pl.col("data_point_time").cast(pl.Datetime))
        .group_by("data_point_time")
        .agg(
            pl.when(pl.col("quantity").is_not_null().all())
            .then(pl.col("quantity").sum())
            .otherwise(pl.lit(None))
            .alias("entso_generation"),
        )
        .sort("data_point_time")
    )

    # interpolate to 1-minute resolution by forward filling
    entso_df = entso_df.upsample("data_point_time", every="1m", maintain_order=True)
    entso_df = entso_df.fill_null(strategy="forward", limit=14)

    # --- Line measurements ---
    line_df_raw = get_line_measurements_from_indirect(
        cfg["indirect_process_object_id"],
        from_ts,
        to_ts,
    ).with_columns(pl.col("phase").cos().alias("power_factor"))

    line_df_raw_filtered = (
        line_df_raw.with_columns(pl.col("realtime").dt.round(every="1m"))
        .pivot(
            on="process_object_id",
            index="realtime",
            values="value",
            aggregate_function="first",
        )
        .drop_nulls()
        .unpivot(
            index="realtime",
            variable_name="process_object_id",
            value_name="value",
        )
        .cast({"process_object_id": pl.Int64})
    )

    line_df_raw_pivot = (
        line_df_raw.with_columns(pl.col("realtime").dt.round(every="1m"))
        .pivot(
            on="process_object_id",
            index="realtime",
            values="value",
            aggregate_function="first",
        )
        .drop_nulls()
    )

    rel_df = get_production_object_ids_from_indirect(cfg["indirect_process_object_id"])

    line_sum = (
        line_df_raw_filtered.join(
            rel_df,
            left_on="process_object_id",
            right_on="direct_process_object_id",
            how="left",
        )
        .with_columns(
            (pl.col("value") * pl.col("primary_calibration_factor")).alias(
                "calibrated_value",
            ),
        )
        .group_by("realtime")
        .agg(pl.col("calibrated_value").sum())
        .sort("realtime")
    )

    combined = line_sum.join(
        entso_df,
        left_on="realtime",
        right_on="data_point_time",
        how="inner",
    )

    # --- Calibration ---
    combined_calibration = line_df_raw_pivot.join(
        entso_df,
        left_on="realtime",
        right_on="data_point_time",
        how="inner",
    ).drop_nulls()

    combined_calibration = combined_calibration.rename({"realtime": "data_point_time"})
    y_var = "entso_generation"
    x_vars = [
        col
        for col in combined_calibration.columns
        if col not in ("data_point_time", y_var)
    ]
    fit_df, param_df = fit_calibration_linear(combined_calibration, y_var, x_vars)

    combined_calibration = combined.join(
        fit_df, left_on="realtime", right_on="data_point_time", how="inner",
    )

    rmse_old = combined_calibration.select(
        (pl.col("entso_generation") - pl.col("calibrated_value")).pow(2).mean().sqrt(),
    )
    rmse_new = combined_calibration.select(
        (pl.col("entso_generation") - pl.col("fit")).pow(2).mean().sqrt(),
    )

    rel_fit_df = rel_df.join(
        param_df,
        on="direct_process_object_id",
    )

    # --- Plotting ---

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=combined_calibration["realtime"],
            y=combined_calibration["entso_generation"],
            mode="lines",
            name="ENTSO-E generation (sum)",
        ),
    )
    fig.add_trace(
        go.Scatter(
            x=combined_calibration["realtime"],
            y=combined_calibration["calibrated_value"],
            mode="lines",
            name="Line measurements (sum)",
        ),
    )
    fig.add_trace(
        go.Scatter(
            x=combined_calibration["realtime"],
            y=combined_calibration["fit"],
            mode="lines",
            name="Fitted generation (linear)",
        ),
    )
    fig.update_layout(
        xaxis_title="Time",
        yaxis_title="Power / Energy",
        hovermode="x unified",
        xaxis_range=[from_ts, to_ts],
    )

    fig_entso_raw = go.Figure()
    for unit, df_unit in entso_df_raw.group_by("unit_name"):
        fig_entso_raw.add_trace(
            go.Scatter(
                x=df_unit["data_point_time"],
                y=df_unit["quantity"],
                mode="lines+markers",
                name=unit[0],
            ),
        )
    fig_entso_raw.update_layout(
        xaxis_title="Time",
        yaxis_title="Generation",
        hovermode="x unified",
        xaxis_range=[from_ts, to_ts],
    )

    fig_line_raw = go.Figure()
    for obj_id, df_obj in line_df_raw_filtered.group_by("process_object_id"):
        fig_line_raw.add_trace(
            go.Scatter(
                x=df_obj["realtime"],
                y=df_obj["value"],
                mode="lines",
                name=str(obj_id[0]),
            ),
        )
    fig_line_raw.update_layout(
        xaxis_title="Time",
        yaxis_title="Measurement value",
        hovermode="x unified",
        xaxis_range=[from_ts, to_ts],
    )

    fig_line_raw_phase = go.Figure()
    for obj_id, df_obj in line_df_raw.group_by("process_object_id"):
        fig_line_raw_phase.add_trace(
            go.Scatter(
                x=df_obj["realtime"],
                y=df_obj["phase"],
                mode="lines",
                name=str(obj_id[0]),
            ),
        )
    fig_line_raw_phase.update_layout(
        xaxis_title="Time",
        yaxis_title="Measurement value",
        title="Phase angle from line measurements",
        hovermode="x unified",
        xaxis_range=[from_ts, to_ts],
    )

    fig_line_raw_power_factor = go.Figure()
    for obj_id, df_obj in line_df_raw.group_by("process_object_id"):
        fig_line_raw_power_factor.add_trace(
            go.Scatter(
                x=df_obj["realtime"],
                y=df_obj["power_factor"],
                mode="lines",
                name=str(obj_id[0]),
            ),
        )
    fig_line_raw_power_factor.update_layout(
        xaxis_title="Time",
        yaxis_title="Measurement value",
        title="Power factor from line measurements",
        hovermode="x unified",
        xaxis_range=[from_ts, to_ts],
    )

    table = html.Table(
        style={"borderCollapse": "collapse", "minWidth": "400px"},
        children=[
            html.Thead(
                html.Tr(
                    [
                        html.Th(
                            "Process object ID",
                            style={"border": "1px solid #ccc", "padding": "6px"},
                        ),
                        html.Th(
                            "Calibration factor",
                            style={"border": "1px solid #ccc", "padding": "6px"},
                        ),
                        html.Th(
                            "New calibration factor",
                            style={"border": "1px solid #ccc", "padding": "6px"},
                        ),
                    ],
                ),
            ),
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td(
                                row["direct_process_object_id"],
                                style={"border": "1px solid #ccc", "padding": "6px"},
                            ),
                            html.Td(
                                row["primary_calibration_factor"],
                                style={"border": "1px solid #ccc", "padding": "6px"},
                            ),
                            html.Td(
                                round(row["b"], 3),
                                style={"border": "1px solid #ccc", "padding": "6px"},
                            ),
                        ],
                    )
                    for row in sorted(
                        rel_fit_df.select(
                            "direct_process_object_id",
                            "primary_calibration_factor",
                            "b",
                        ).to_dicts(),
                        key=lambda x: x["direct_process_object_id"],
                    )
                ],
            ),
        ],
    )

    error_table = html.Table(
        style={"borderCollapse": "collapse"},
        children=[
            html.Thead(
                html.Tr(
                    [
                        html.Th(
                            "Metric",
                            style={"border": "1px solid #ccc", "padding": "6px"},
                        ),
                        html.Th(
                            "Value",
                            style={"border": "1px solid #ccc", "padding": "6px"},
                        ),
                    ],
                ),
            ),
            html.Tbody(
                [
                    html.Tr(
                        [
                            html.Td(
                                "RMSE before calibration",
                                style={"border": "1px solid #ccc", "padding": "6px"},
                            ),
                            html.Td(
                                round(rmse_old[0, 0], 0),
                                style={
                                    "border": "1px solid #ccc",
                                    "padding": "6px",
                                    "text-align": "right",
                                },
                            ),
                        ],
                    ),
                    html.Tr(
                        [
                            html.Td(
                                "RMSE after calibration",
                                style={"border": "1px solid #ccc", "padding": "6px"},
                            ),
                            html.Td(
                                round(rmse_new[0, 0], 0),
                                style={
                                    "border": "1px solid #ccc",
                                    "padding": "6px",
                                    "text-align": "right",
                                },
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )

    sql_output = generate_sql_update(
        param_df,
        indirect_process_object_id=cfg["indirect_process_object_id"],
    )

    return (
        fig,
        fig_entso_raw,
        fig_line_raw,
        fig_line_raw_phase,
        fig_line_raw_power_factor,
        table,
        error_table,
        sql_output,
    )


if __name__ == "__main__":
    app.run(debug=False, port=8080)
