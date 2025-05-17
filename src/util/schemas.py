import polars

study_time_schema = {
    "timestamp": polars.Datetime("us"),
    "studied_seconds": polars.Int32,
}
