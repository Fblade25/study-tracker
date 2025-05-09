from components.sidebar import Sidebar
from pages.home_page import HomePage
from pages.statistics_page import StatisticsPage
from pages.study_page import StudyPage
from PySide6.QtWidgets import QHBoxLayout, QMainWindow, QStackedWidget, QWidget


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Study Tracker")
        self.setGeometry(100, 100, 920, 640)

        # Create sidebar
        self.sidebar = Sidebar(self)

        # Create stacked widget for content area
        self.stacked_widget = QStackedWidget(self)

        # Create pages for the stacked widget
        self.page_home = HomePage()
        self.page_study = StudyPage()
        self.page_statistics = StatisticsPage()

        # Add pages to stacked widget
        self.stacked_widget.addWidget(self.page_home)
        self.stacked_widget.addWidget(self.page_study)
        self.stacked_widget.addWidget(self.page_statistics)

        # Create layout to manage sidebar and content area
        central_widget = QWidget(self)
        central_layout = QHBoxLayout(central_widget)
        central_layout.addWidget(self.sidebar)  # Sidebar on the left
        central_layout.addWidget(self.stacked_widget)  # Stacked widget on the right
        self.setCentralWidget(central_widget)

        # Connect sidebar buttons to switch pages in the stacked widget
        self.sidebar.button_home.clicked.connect(lambda: self.switch_page(0))
        self.sidebar.button_study.clicked.connect(lambda: self.switch_page(1))
        self.sidebar.button_statistics.clicked.connect(lambda: self.switch_page(2))

    def switch_page(self, index):
        """Switch pages in the stacked widget"""
        self.stacked_widget.setCurrentIndex(index)
