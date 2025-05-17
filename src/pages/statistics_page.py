from components.dropdown import SubjectDropdown
from PySide6.QtWidgets import QVBoxLayout, QWidget


class StatisticsPage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)

        self.subject_dropdown = SubjectDropdown()
        self.subject_dropdown.load_subjects_in_dropdown()
        layout.addWidget(self.subject_dropdown)
