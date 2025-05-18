from PySide6.QtCore import Qt
from PySide6.QtWidgets import QPushButton, QVBoxLayout, QWidget


class Sidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Sidebar")

        # Sidebar layout and widget
        self.setLayout(QVBoxLayout(self))

        # Configure sidebar layout
        self.setFixedWidth(200)
        self.layout().setContentsMargins(0, 0, 0, 0)
        self.layout().setSpacing(10)
        self.layout().setAlignment(Qt.AlignTop)

        # Add a collapse button to toggle visibility
        self.button_toggle = QPushButton("Collapse")
        self.set_button_style(self.button_toggle)
        self.layout().addWidget(self.button_toggle)

        # Connect the collapse button to a method that hides/shows the sidebar
        self.button_toggle.clicked.connect(self.toggle_sidebar)

        # Create navigation buttons
        self.button_home = QPushButton("Home")
        self.button_study = QPushButton("Study")
        self.button_statistics = QPushButton("Statistics")

        # Set button styles
        self.set_button_style(self.button_home)
        self.set_button_style(self.button_study)
        self.set_button_style(self.button_statistics)

        # Add buttons to sidebar layout
        self.layout().addWidget(self.button_home)
        self.layout().addWidget(self.button_study)
        self.layout().addWidget(self.button_statistics)

    def set_button_style(self, button: QPushButton) -> None:
        """Sets button size."""
        button.setMinimumHeight(50)
        button.setMaximumHeight(50)

    def toggle_sidebar(self) -> None:
        """Expands or closes sidebar."""
        main_window = self.window()
        old_pos = main_window.pos()
        width = main_window.width()
        height = main_window.height()
        delta = 0

        # Collapse or expand sidebar
        if self.width() > 50:
            self.setFixedWidth(50)
            delta = -150
        else:
            self.setFixedWidth(200)
            delta = 150

        # Resize window and move
        main_window.resize(width + delta, height)
        main_window.move(old_pos)
