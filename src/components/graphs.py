import os
import tempfile

import plotly.express as px
import plotly.io as pio
import polars
from PySide6.QtCore import QUrl
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import QVBoxLayout, QWidget


class TimeSeriesGraphWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.view = QWebEngineView()
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.view)
        self.setLayout(self.layout)

    def load_data(self, df: polars.DataFrame, title: str):
        """Create HTML plot based on provided data."""
        # Force software rendering
        os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = (
            "--disable-gpu --disable-software-rasterizer"
        )
        os.environ["QT_QUICK_BACKEND"] = "software"
        # Create plot
        fig = px.bar(
            df,
            x="timestamp",
            y="studied_minutes",
            title=title,
            template="plotly_white",
        )

        fig.update_xaxes(rangeslider_visible=True)
        fig.update_layout(transition_duration=500)

        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as f:
            pio.write_html(fig, file=f.name, auto_open=False)
            self.view.load(QUrl.fromLocalFile(f.name))
