import datetime

import polars
from components.graphs import PieChartWidget
from PySide6.QtWidgets import QVBoxLayout, QWidget
from util.util import get_all_subjects, get_processed_df_from_subject


class HomePage(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)

        self.total_study_time_pie_chart = PieChartWidget(self)
        self.layout.addWidget(self.total_study_time_pie_chart)

        self.update_plots()

    def update_plots(self, reset=False):
        """Updates plots on this page."""
        all_subjects = get_all_subjects()

        if all_subjects:
            dfs: dict[str, polars.DataFrame] = {}
            timestamp_end = datetime.datetime.now() + datetime.timedelta(days=1)

            for subject in all_subjects:
                dfs[subject] = get_processed_df_from_subject(
                    subject, timestamp_end=timestamp_end
                )

            if reset:
                self.total_study_time_pie_chart.reset_values()

            self.total_study_time_pie_chart.load_data(dfs)
