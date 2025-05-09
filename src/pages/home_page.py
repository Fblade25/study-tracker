from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget


class HomePage(QWidget):
    def __init__(self):
        super().__init__()

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Welcome to the Home page"))
