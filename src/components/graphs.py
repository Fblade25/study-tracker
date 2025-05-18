import polars
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtWidgets import QVBoxLayout, QWidget
from styles.colors import Colors
from util.util import set_xaxis_labels


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

        self._bars = None
        self._animation = None

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

        self._timestamps = timestamps
        self._values = values

        self._bars = ax.bar(
            timestamps,
            [0] * len(values),
            color=self.colors["bar"],
            edgecolor=self.colors["bar_edge"],
            linewidth=0.5,
            width=self.get_bar_width(timestamps),
        )

        ax.set_title(title, color=self.colors["text"])
        ax.set_xlabel("Timestamp", color=self.colors["text"])
        ax.set_ylabel("Studied Minutes", color=self.colors["text"])

        max_value = max(values) if values else 1
        ax.set_ylim(0, max_value * 1.1)

        ax.tick_params(axis="x", colors=self.colors["text"])
        ax.tick_params(axis="y", colors=self.colors["text"])

        # Use custom formatter for x-labels
        set_xaxis_labels(ax, timestamps)

        # Grid color
        ax.grid(True, axis="y", color=self.colors["grid"])

        # Animate
        self._animation = FuncAnimation(
            self.figure,
            self.animate,
            frames=30,
            interval=1000 // 60,
            blit=False,
            repeat=False,
        )

        self.canvas.draw()

    def ease_in_out_quad(self, frame):
        if frame < 0.5:
            return 2 * frame * frame
        return -1 + (4 - 2 * frame) * frame

    def animate(self, i):
        frames = 30
        frame = i / frames
        eased_t = self.ease_in_out_quad(frame)
        for bar, value in zip(self._bars, self._values, strict=False):
            bar.set_height(eased_t * value)
        return self._bars
