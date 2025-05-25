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

        self._values = None
        self._previous_values = None

        self._ax = None
        self._bars = None
        self._animation = None
        self._ylim = None

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
            range_days = (max(timestamps) - min(timestamps)).total_seconds() / 86400
            spacing = range_days / (len(timestamps) - 1)
            bar_width = spacing * 0.9
            return bar_width
        return 1.0

    def reset_values(self):
        """Resets certain values when changing data source."""
        self._ax = None
        self._bars = None
        self._animation = None
        self._values = None
        self._max_value = None
        self._previous_values = None
        self._ylim = None
        self.figure.clear()

    def aggregate_data(
        self, df: polars.DataFrame, zoom_level: str
    ) -> tuple[polars.DataFrame, str]:
        """Aggregates data for plotting based on zoom level."""

        if zoom_level in ("Week", "Month"):
            # Group by date, sum studied_hours as 'value'
            grouped = (
                df.group_by("date")
                .agg(polars.col("studied_hours").sum().alias("value"))
                .sort("date")
                .with_columns(
                    polars.col("date").cast(polars.Datetime).alias("timestamp")
                )
                .select(["timestamp", "value"])
            )
            return grouped, "Hours"

        elif zoom_level == "Year":
            if "year" not in df.columns:
                raise ValueError(
                    "DataFrame must have 'year' column for 'Year' zoom level"
                )

            grouped = (
                df.group_by(["year", "month"])
                .agg(polars.col("studied_hours").sum().alias("value"))
                .sort(["year", "month"])
            )

            grouped = grouped.with_columns(
                (
                    polars.col("year").cast(str)
                    + "-"
                    + polars.col("month").cast(str).str.zfill(2)
                    + "-01"
                )
                .str.strptime(polars.Datetime, "%Y-%m-%d")
                .alias("timestamp")
            ).select(["timestamp", "value"])

            return grouped, "Hours"

        else:
            # No aggregation, just rename studied_minutes to value
            df = df.with_columns(polars.col("studied_minutes").alias("value"))
            return df.sort("timestamp").select(["timestamp", "value"]), "Minutes"

    def load_data(self, df: polars.DataFrame, title: str, zoom_level: str):
        """Loads data for plotting."""

        df, ylabel = self.aggregate_data(df, zoom_level)

        timestamps = df["timestamp"].to_list()
        values = df["value"].to_list()

        self._max_value = max(values) if values else 1

        self._timestamps = timestamps
        self._values = values

        ylim_changed = False
        if self._ylim is None or self._ylim * 0.9 < self._max_value:
            self._ylim = max(self._max_value * 1.1, 1)
            ylim_changed = True

        if self._ax is None:
            self._ax = self.figure.add_subplot(111, facecolor=self.colors["background"])

            # Labels
            self._ax.set_title(title, color=self.colors["text"])
            self._ax.set_xlabel("Timestamp", color=self.colors["text"])

            self._ax.set_ylabel(ylabel, color=self.colors["text"])

            # Scope
            self._ax.set_ylim(0, self._ylim)

            # Ticks
            self._ax.tick_params(axis="x", colors=self.colors["text"])
            self._ax.tick_params(axis="y", colors=self.colors["text"])

            # Grid color
            self._ax.grid(True, axis="y", color=self.colors["grid"])

            # Use custom formatter for x-labels
            set_xaxis_labels(self._ax, timestamps, zoom_level)

        if ylim_changed:
            self._ax.set_ylim(0, self._ylim)
            self.canvas.draw()

        if self._previous_values is None:
            self._previous_values = [0] * len(values)
        else:
            self._previous_values = self._values
            # Match size
            if len(self._previous_values) < len(self._values):
                self._previous_values = self._previous_values + [0] * (
                    len(self._values) - len(self._previous_values)
                )

        self._bars = self._ax.bar(
            timestamps,
            self._previous_values,
            color=self.colors["bar"],
            edgecolor=self.colors["bar_edge"],
            linewidth=0.5,
            width=self.get_bar_width(timestamps),
        )

        # Animate
        self._animation = FuncAnimation(
            self.figure,
            self.animate,
            frames=30,
            interval=1000 // 60,
            blit=True,
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
        for bar, value, previous_value in zip(
            self._bars, self._values, self._previous_values, strict=False
        ):
            delta = value - previous_value
            height = eased_t * delta + previous_value
            bar.set_height(height)
        return self._bars
