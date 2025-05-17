import datetime

import polars
from components.clock import Clock
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from util.constants import DATA_FILE
from util.schemas import study_time_schema
from util.util import get_data_path


class StudyPage(QWidget):
    def __init__(self):
        super().__init__()

        self.__timer = QTimer(self)
        self.__timer.timeout.connect(self.timer_update)

        # Variables
        self.is_timing = False
        self.start_time = datetime.datetime.now()
        self.stop_time = datetime.datetime.now()
        self.minutes = 0
        self.hours = 0
        self.current_subject = "General"

        layout = QVBoxLayout(self)

        # Add subject functionality
        subject_layout = QHBoxLayout()

        self.subject_dropdown = QComboBox()
        self.load_subjects_in_dropdown()

        add_subject_button = QPushButton("Add subject")
        add_subject_button.clicked.connect(self.add_subject_form)

        subject_layout.addWidget(self.subject_dropdown)
        subject_layout.addWidget(add_subject_button)

        # Vertical layout
        layout.addLayout(subject_layout)

        self.timer_button = QPushButton("Start")
        layout.addWidget(self.timer_button)

        self.clock: Clock = Clock(self)
        layout.addWidget(self.clock)

        # Connect events
        self.timer_button.clicked.connect(self.timer_button_event)

    def load_subjects_in_dropdown(self) -> None:
        """Reloads subjects in the dropdown menu."""
        parquet_files = [
            file.name for file in get_data_path().iterdir() if file.suffix == ".parquet"
        ]
        self.subject_dropdown.clear()

        # Make general subject if there is none
        if len(parquet_files) == 0:
            self.save_subject("General")

        # Load each subject
        for file_name in parquet_files:
            subject_name = file_name.replace(".parquet", "")
            self.subject_dropdown.addItem(subject_name)

        # Preselect subject
        index = self.subject_dropdown.findText(self.current_subject)
        if index != -1:
            self.subject_dropdown.setCurrentIndex(index)

    def save_subject(self, subject_name: str) -> None:
        """Adds new .parquet file to data folder."""
        path = get_data_path() / DATA_FILE.format(subject_name=subject_name)

        if not path.exists():
            # Create empty DataFrame
            df = polars.DataFrame(schema=study_time_schema)

            # Save DataFrame
            df.write_parquet(path)

            # Reload drop down
            self.current_subject = subject_name
            self.load_subjects_in_dropdown()

    def add_subject_form(self, event) -> None:
        """Opens form to add subject."""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add subject")
        dialog.setMaximumWidth(300)

        layout = QVBoxLayout(dialog)
        form_layout = QFormLayout()

        # Input
        subject_input = QLineEdit()
        form_layout.addRow("Subject name:", subject_input)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)

        # Layout
        layout.addLayout(form_layout)
        layout.addWidget(button_box)

        # Execute dialog
        if dialog.exec_() == QDialog.Accepted:
            subject_name = subject_input.text().strip()
            if subject_name:
                self.save_subject(subject_name)

    def save_data(self, datetime: datetime.datetime, seconds: int) -> None:
        """Saves study data into parquet file."""
        path = get_data_path() / DATA_FILE.format(subject_name=self.current_subject)

        # Open DataFrame
        df = polars.read_parquet(path)

        # Filter relevant row
        existing_row = df.filter(polars.col("timestamp") == datetime)

        # Collect second data if row exists
        if existing_row.height > 0:
            seconds = existing_row["studied_seconds"][0] + float(seconds)

        # Filter out the row that already exists
        df = df.filter(polars.col("timestamp") != datetime)

        # Create new row
        new_row = polars.DataFrame(
            data=[[datetime, seconds]], schema=study_time_schema, orient="row"
        )

        # Save data
        df = polars.concat([df, new_row])
        df = df.sort("timestamp")

        # Write to file
        df.write_parquet(path)

    def timer_update(self, save: bool = False) -> None:
        """Calculate amount time passed up to now."""
        self.stop_time = datetime.datetime.now()
        seconds = (self.stop_time - self.start_time).total_seconds()

        # Save every minute is crossed
        if self.stop_time.second == 0 or save:
            save_date = self.stop_time - datetime.timedelta(minutes=1)
            save_date = save_date.replace(minute=0, second=0, microsecond=0)
            self.save_data(save_date, int(seconds))

            # Reset second counter
            self.start_time = datetime.datetime.now()
            self.stop_stop = datetime.datetime.now()

    def timer_button_event(self, event) -> None:
        """Start/stop timer and change text of button."""
        if self.is_timing:  # Stop timer
            self.timer_update(save=True)  # Force save
            self.__timer.stop()
            self.timer_button.setText("Start")
            self.is_timing = False
            self.clock.reset_times()
        else:  # Start timer
            self.__timer.start(1000)  # Every second
            self.start_time = datetime.datetime.now()
            self.timer_button.setText("Stop")
            self.is_timing = True
            self.clock.set_start_time(self.start_time)
