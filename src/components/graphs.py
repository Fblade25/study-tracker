import matplotlib.dates as mdates
import polars
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtWidgets import QVBoxLayout, QWidget
from styles.colors import Colors


class TimeSeriesGraphWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.colors = self.get_colors()

        self.figure = Figure(facecolor=self.colors["background"])
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet(f"background-color: {self.colors['background']};")

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.canvas)
        self.setLayout(self.layout)

        # Set widget background
        # self.setAutoFillBackground(True)

    def get_colors(self) -> dict[str, str]:
        """Returns a dictionary of theme colors."""
        return {
            "background": Colors.BACKGROUND,
            "text": Colors.TEXT,
            "grid": Colors.BORDER_COLOR,
            "bar": Colors.BUTTON_HOVER,
            "bar_edge": Colors.PRIMARY,
        }

    def get_bar_width(self, timestamps: list[polars.Datetime]) -> float:
        """Calculates bar width based on timestamp range."""
        if len(timestamps) > 1:
            range_days = (timestamps[-1] - timestamps[0]).total_seconds() / 86400
            spacing = range_days / (len(timestamps) - 1)
            bar_width = spacing * 0.9
            return bar_width
        return 1.0

    def load_data(self, df: polars.DataFrame, title: str):
        self.figure.clear()
        ax = self.figure.add_subplot(111, facecolor=self.colors["background"])

        # Convert Polars timestamps to matplotlib dates
        timestamps = df["timestamp"].to_list()
        values = df["studied_minutes"].to_list()

        ax.bar(
            timestamps,
            values,
            color=self.colors["bar"],
            edgecolor=self.colors["bar_edge"],
            linewidth=0.5,
            width=self.get_bar_width(timestamps),
        )

        ax.set_title(title, color=self.colors["text"])
        ax.set_xlabel("Timestamp", color=self.colors["text"])
        ax.set_ylabel("Studied Minutes", color=self.colors["text"])

        ax.tick_params(axis="x", colors=self.colors["text"])
        ax.tick_params(axis="y", colors=self.colors["text"])

        # Format x-axis for dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
        self.figure.autofmt_xdate()

        ax.grid(True, axis="y", color=self.colors["grid"])
        self.canvas.draw()
