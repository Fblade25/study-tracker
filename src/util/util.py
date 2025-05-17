import os
import pathlib
import sys

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
