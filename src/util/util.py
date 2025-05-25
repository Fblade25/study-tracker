import datetime
import os
import pathlib
import sys

import matplotlib.dates as mdates
from matplotlib.ticker import FuncFormatter
from util.constants import DATA_DIR


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
