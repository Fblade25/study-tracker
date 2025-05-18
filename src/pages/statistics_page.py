import datetime

import polars
from components.dropdown import SubjectDropdown
from components.graphs import TimeSeriesGraphWidget
from PySide6.QtWidgets import QVBoxLayout, QWidget
from util.constants import DATA_FILE
from util.util import get_data_path


class StatisticsPage(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)

        self.subject_dropdown = SubjectDropdown()
        self.subject_dropdown.load_subjects_in_dropdown()
        self.subject_dropdown.currentIndexChanged.connect(self.update_plots)
        self.layout.addWidget(self.subject_dropdown)

        self.study_time_graph = TimeSeriesGraphWidget(self)
        self.layout.addWidget(self.study_time_graph)

    def update_subject_list(self):
        self.subject_dropdown.load_subjects_in_dropdown(
            self.subject_dropdown.get_current_subject()
        )

    def preprocess_data(self, df: polars.DataFrame):
        """Preprocesses the data."""
        df = df.with_columns(
            (polars.col("studied_seconds") / 60).alias("studied_minutes")
        )
        if len(df) != 0:
            ts_min = df["timestamp"].min()
            ts_max = df["timestamp"].max()

            # Add timestamp data for hours
            hours = []
            current = ts_min
            while current <= ts_max:
                hours.append(current)
                current += datetime.timedelta(hours=1)

            full_range = polars.DataFrame({"timestamp": hours})

            # Fill missing values with 0
            joined = full_range.join(df, on="timestamp", how="left")
            joined = joined.with_columns(polars.col("studied_minutes").fill_null(0))
            return joined
        return df

    def update_plots(self):
        """"""
        subject = self.subject_dropdown.get_current_subject()

        if subject:
            data_path = get_data_path() / DATA_FILE.format(subject_name=subject)

            df = polars.read_parquet(data_path)

            df_processed = self.preprocess_data(df)

            self.study_time_graph.load_data(df_processed, "Study time")
