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


def get_date_formatter(timestamps):
    # Return a formatter that just returns empty labels if no data
    if not timestamps:
        return FuncFormatter(lambda x, _: "")

    # Convert timestamps to naive dates for comparison
    dates = [timestamp.date() for timestamp in timestamps]

    def formatter(x, _):
        datetime = mdates.num2date(x).replace(tzinfo=None)
        closest_idx = min(
            range(len(timestamps)), key=lambda i: abs(timestamps[i] - datetime)
        )
        # Check if this tick is the first or a new day boundary
        if closest_idx == 0 or (
            closest_idx > 0 and dates[closest_idx] != dates[closest_idx - 1]
        ):
            return datetime.strftime("%b %d %H:%M")  # e.g. May 18 18:00
        else:
            return datetime.strftime("%H:%M")  # just time

    return FuncFormatter(formatter)
