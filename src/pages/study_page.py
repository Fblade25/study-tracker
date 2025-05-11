import datetime

from components.clock import Clock
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget


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

        layout = QVBoxLayout(self)

        self.timer_button = QPushButton("Start")
        layout.addWidget(self.timer_button)

        clock = Clock(self)
        layout.addWidget(clock)

        # Connect events
        self.timer_button.clicked.connect(self.timer_button_event)

    def save_data(self) -> None:
        pass

    def timer_update(self) -> None:
        """Calculate amount time passed up to now."""
        self.stop_time = datetime.datetime.now()
        seconds = (self.stop_time - self.start_time).total_seconds()
        self.minutes = int((seconds + 59) // 60)  # rounding errors
        print(f"minutes: {self.minutes}.")

    def timer_button_event(self, event) -> None:
        """Start/stop timer and change text of button."""
        if self.is_timing:
            self.__timer.stop()
            self.timer_button.setText("Start")
            self.is_timing = False
        else:
            self.__timer.start(1000 * 60)  # Every minute
            self.start_time = datetime.datetime.now()
            self.timer_button.setText("Stop")
            self.is_timing = True
