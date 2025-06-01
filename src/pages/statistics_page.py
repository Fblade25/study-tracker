import datetime

from components.dropdown import SubjectDropdown
from components.graphs import BarPlotWidget
from dateutil.relativedelta import relativedelta
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QButtonGroup,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from util.util import get_processed_df_from_subject


class StatisticsPage(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout(self)

        self.subject_dropdown = SubjectDropdown()
        self.subject_dropdown.load_subjects_in_dropdown()
        self.subject_dropdown.currentIndexChanged.connect(
            lambda: self.update_plots(True)
        )
        self.layout.addWidget(self.subject_dropdown)

        self.timestamp_start: datetime.datetime | None = None
        self.timestamp_end: datetime.datetime | None = None
        self.zoom_delta = None

        # Add navigation buttons
        zoom_layout = QHBoxLayout()
        button_left = QPushButton("◄")
        button_right = QPushButton("►")
        button_left.clicked.connect(lambda: self.move_zoom_level("left"))
        button_right.clicked.connect(lambda: self.move_zoom_level("right"))

        zoom_layout.addWidget(button_left)
        self.zoom_buttons = QButtonGroup(self)
        for label in ["Day", "Week", "Month", "Year"]:
            button = QPushButton(label)
            button.setCheckable(True)
            zoom_layout.addWidget(button)
            self.zoom_buttons.addButton(button)

        self.zoom_buttons.buttonClicked.connect(self.set_zoom_level)
        self.zoom_buttons.buttons()[0].setChecked(True)

        zoom_layout.addWidget(button_right)
        self.layout.addLayout(zoom_layout)

        # Add label for current range
        self.date_range_label = QLabel("")
        font = QFont()
        font.setPointSize(30)
        font.setWeight(QFont.Bold)
        self.date_range_label.setFont(font)
        self.date_range_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.date_range_label)

        # Add plot widgets
        self.study_time_bar_plot = BarPlotWidget(self)
        self.layout.addWidget(self.study_time_bar_plot)

        # Set default to days
        self.set_zoom_level(self.zoom_buttons.buttons()[0])

    def update_subject_list(self) -> None:
        self.subject_dropdown.load_subjects_in_dropdown(
            self.subject_dropdown.get_current_subject()
        )

    def update_date_range_label(self) -> None:
        """Updates the label of the date range."""
        zoom_level = self.zoom_buttons.checkedButton().text()
        if zoom_level == "Day":
            fmt = "%b %d, %Y"
        elif zoom_level == "Week":
            fmt = "%b %d, %Y"
            text = f"{self.timestamp_start.strftime(fmt)} \
- {self.timestamp_end.strftime(fmt)}"
            self.date_range_label.setText(text)
            return
        elif zoom_level == "Month":
            fmt = "%b %Y"
        elif zoom_level == "Year":
            fmt = "%Y"
        else:
            fmt = "%Y-%m-%d"
        text = f"{self.timestamp_start.strftime(fmt)}"
        self.date_range_label.setText(text)

    def move_zoom_level(self, direction: str) -> None:
        """Moves the zoom level left or right."""
        if direction == "left":
            self.timestamp_start -= self.zoom_delta
            self.timestamp_end -= self.zoom_delta
        else:
            self.timestamp_start += self.zoom_delta
            self.timestamp_end += self.zoom_delta
        self.update_date_range_label()
        self.update_plots(reset=True)

    def set_zoom_level(self, button: QPushButton) -> None:
        """Changes the zoom level of which data to view."""
        zoom = button.text()
        current_day = datetime.datetime.now().replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        # Set start and end time
        match zoom:
            case "Day":
                self.zoom_delta = datetime.timedelta(days=1)
                self.timestamp_start = current_day
            case "Week":
                self.zoom_delta = datetime.timedelta(days=7)
                self.timestamp_start = current_day - datetime.timedelta(
                    days=current_day.weekday()
                )
            case "Month":
                self.zoom_delta = relativedelta(months=1)
                self.timestamp_start = current_day.replace(day=1)
            case "Year":
                self.zoom_delta = relativedelta(years=1)
                self.timestamp_start = current_day.replace(month=1, day=1)
        self.timestamp_end = self.timestamp_start + self.zoom_delta
        # Update data
        self.update_date_range_label()
        self.update_plots(reset=True)

    def update_plots(self, reset=False):
        """Updates plots on this page."""
        subject = self.subject_dropdown.get_current_subject()

        if subject:
            df_processed = get_processed_df_from_subject(
                subject, self.timestamp_start, self.timestamp_end
            )

            if reset:
                self.study_time_bar_plot.reset_values()

            # Update plots
            zoom_level = self.zoom_buttons.checkedButton().text()
            self.study_time_bar_plot.load_data(df_processed, "Study time", zoom_level)
