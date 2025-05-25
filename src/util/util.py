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


def custom_date_formatter(timestamps):
    # Return a formatter that just returns empty labels if no data
    if not timestamps:
        return FuncFormatter(lambda x, _: "")

    # Convert timestamps to naive dates for comparison
    dates = [timestamp.date() for timestamp in timestamps]

    def formatter(x, _):
        datetime = mdates.num2date(x).replace(tzinfo=None)
        closest_index = min(
            range(len(timestamps)), key=lambda i: abs(timestamps[i] - datetime)
        )
        # Check if this tick is the first or a new day boundary
        if closest_index == 0 or (
            closest_index > 0 and dates[closest_index] != dates[closest_index - 1]
        ):
            return datetime.strftime("%b %d %H:%M")  # e.g. May 18 18:00
        else:
            return datetime.strftime("%H:%M")  # just time

    return FuncFormatter(formatter)


def set_xaxis_labels(ax, timestamps):
    # Set the formatter
    ax.xaxis.set_major_formatter(custom_date_formatter(timestamps))

    # Start by getting the locations matplotlib chooses
    locs = ax.get_xticks()

    # Find the closest timestamp for each tick location
    def find_closest_index(x):
        return min(
            range(len(timestamps)),
            key=lambda i: abs(timestamps[i] - mdates.num2date(x).replace(tzinfo=None)),
        )

    closest_indexes = []
    if timestamps:
        closest_indexes = [find_closest_index(x) for x in locs]

    # Mark ticks at midnightimestamp (hour=0, min=0)
    midnight_indexes = [
        i
        for i, timestamp in enumerate(timestamps)
        if timestamp.hour == 0 and timestamp.minute == 0
    ]

    # Keep midnight ticks, and then add others spaced evenly but not too close
    max_ticks = 5
    non_midnight_indexes = sorted(set(closest_indexes) - set(midnight_indexes))

    remaining_slots = max_ticks - len(midnight_indexes)
    if remaining_slots > 0 and non_midnight_indexes:
        step = max(1, len(non_midnight_indexes) // (max_ticks - len(midnight_indexes)))
        selected_non_midnight = non_midnight_indexes[::step]
    else:
        selected_non_midnight = []

    selected_indexes = sorted(set(midnight_indexes + selected_non_midnight))

    # Get positions for these indices
    selected_locs = [mdates.date2num(timestamps[i]) for i in selected_indexes]

    ax.set_xticks(selected_locs)
    ax.tick_params(axis="x", rotation=30)
