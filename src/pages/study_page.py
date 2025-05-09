from components.clock import Clock
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class StudyPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Welcome to the Study page!"))

        clock = Clock(self)
        layout.addWidget(clock)
