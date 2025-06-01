import datetime
import os
import pathlib
import sys

import matplotlib.dates as mdates
import polars
from matplotlib.ticker import FuncFormatter
from util.constants import DATA_DIR, DATA_FILE


def get_data_path() -> pathlib.Path:
    base_data_dir: pathlib.Path
    if sys.platform == "win32":
        appdata_dir = os.getenv("LOCALAPPDATA") or os.getenv("APPDATA")
        base_data_dir = pathlib.Path(appdata_dir) / "StudyTracker" / DATA_DIR
    else:
        base_data_dir = (
            pathlib.Path.home() / ".local" / "share" / "StudyTracker" / DATA_DIR
        )

    # Ensure directory exists
    base_data_dir.mkdir(parents=True, exist_ok=True)

    return base_data_dir


def get_all_subjects() -> list[str]:
    path = get_data_path()
    subjects = [p.stem for p in path.glob("*.parquet")]
    return subjects


def preprocess_data(
    df: polars.DataFrame,
    timestamp_start: datetime.datetime | None,
    timestamp_end: datetime.datetime | None,
) -> polars.DataFrame:
    """Preprocesses the data."""

    df = df.with_columns(
        [
            (polars.col("studied_seconds") / 60).alias("studied_minutes"),
            (polars.col("studied_seconds") / 3600).alias("studied_hours"),
        ]
    )

    if len(df) != 0:
        # Filter timestamps
        if timestamp_start is not None:
            df = df.filter(polars.col("timestamp") >= timestamp_start)
        else:
            timestamp_start = df["timestamp"].min()

        if timestamp_end is not None:
            df = df.filter(polars.col("timestamp") < timestamp_end)
        else:
            timestamp_end = df["timestamp"].max()

        # Add timestamp data for hours
        hours = []
        current = timestamp_start
        while current < timestamp_end:
            hours.append(current)
            current += datetime.timedelta(hours=1)

        full_range = polars.DataFrame({"timestamp": hours})

        # Fill missing values with 0
        joined = full_range.join(df, on="timestamp", how="left")
        joined = joined.with_columns(
            [
                polars.col("studied_seconds").fill_null(0),
                polars.col("studied_minutes").fill_null(0),
                polars.col("studied_hours").fill_null(0),
            ]
        )
        # Add fields to be able to group by date, month, and year
        joined = joined.with_columns(
            [
                polars.col("timestamp").dt.date().alias("date"),
                polars.col("timestamp").dt.month().alias("month"),
                polars.col("timestamp").dt.year().alias("year"),
            ]
        )
        return joined
    return df


def get_processed_df_from_subject(
    subject: str, timestamp_start=None, timestamp_end=None
):
    """Returns processed DataFrame of subject."""
    data_path = get_data_path() / DATA_FILE.format(subject_name=subject)

    df = polars.read_parquet(data_path)

    df_processed = preprocess_data(df, timestamp_start, timestamp_end)

    return df_processed


def custom_date_formatter(timestamps: list[datetime.datetime], zoom_level: str):
    # Defensive empty check
    if not timestamps:
        return FuncFormatter(lambda x, _: "")

    def formatter(x, _):
        dt = mdates.num2date(x).replace(tzinfo=None)

        if zoom_level == "Day":
            # Show hour
            return dt.strftime("%H")

        elif zoom_level == "Week":
            # Show weekday name
            return dt.strftime("%A")

        elif zoom_level == "Month":
            # Show just month and day
            return dt.strftime("%d")

        elif zoom_level == "Year":
            # Show month and year
            return dt.strftime("%b")

        else:
            return dt.strftime("%Y-%m-%d %H:%M")

    return FuncFormatter(formatter)


def set_xaxis_labels(ax, timestamps: list[datetime.datetime], zoom_level: str):
    ax.xaxis.set_major_formatter(custom_date_formatter(timestamps, zoom_level))

    if not timestamps:
        return

    max_ticks = 12

    if zoom_level == "Day":
        # For day zoom, show hourly ticks (assumed timestamps cover the day hourly)
        start = timestamps[0].replace(minute=0, second=0, microsecond=0)
        end = timestamps[-1].replace(minute=0, second=0, microsecond=0)
        hours = []
        current = start
        while current <= end:
            hours.append(current)
            current += datetime.timedelta(hours=1)
        ax.set_xticks([mdates.date2num(h) for h in hours])
        ax.tick_params(axis="x", rotation=30)
        return

    # For other zoom levels, pick evenly spaced ticks from timestamps
    n = len(timestamps)
    if n <= max_ticks:
        selected_indexes = list(range(n))
    else:
        step = n // max_ticks
        selected_indexes = list(range(0, n, step))
        # Make sure last index is included
        if selected_indexes[-1] != n - 1:
            selected_indexes.append(n - 1)

    selected_locs = [mdates.date2num(timestamps[i]) for i in selected_indexes]

    ax.set_xticks(selected_locs)
    ax.tick_params(axis="x", rotation=30)
