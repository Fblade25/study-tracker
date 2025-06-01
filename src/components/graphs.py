import polars
from matplotlib.animation import FuncAnimation
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtWidgets import QVBoxLayout, QWidget
from styles.colors import Colors
from util.util import ease_in_out_quad, set_xaxis_labels


class AbstractPlotWidget(QWidget):
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

    def get_colors(self) -> dict[str, str]:
        """Returns a dictionary of theme colors."""
        return {
            "background": Colors.BACKGROUND,
            "text": Colors.TEXT,
            "grid": Colors.BORDER_COLOR,
            "bar": Colors.BUTTON_HOVER,
            "bar_edge": Colors.PRIMARY,
        }

    def reset_values(self):
        """Should reset certain values when changing data source."""
        pass

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


class BarPlotWidget(AbstractPlotWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._bars = None
        self._animation = None
        self._ylim = None

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

    def load_data(self, df: polars.DataFrame, title: str, zoom_level: str):
        """Loads data for plotting."""

        df, ylabel = self.aggregate_data(df, zoom_level)

        timestamps = df["timestamp"].to_list()
        values = df["value"].to_list()

        self._max_value = max(values) if values else 1

        self._timestamps = timestamps

        # Save current values as previous before updating
        if self._values is None:
            self._previous_values = [0] * len(values)
        else:
            # Keep old values as previous
            self._previous_values = self._values

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

    def animate(self, i):
        frames = 30
        frame = i / frames
        eased_t = ease_in_out_quad(frame)
        for bar, value, previous_value in zip(
            self._bars, self._values, self._previous_values, strict=False
        ):
            delta = value - previous_value
            height = eased_t * delta + previous_value
            bar.set_height(height)
        return self._bars


class PieChartWidget(AbstractPlotWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self._previous_total_hours = 0.0
        self._total_hours = 0.0

    def reset_values(self):
        """Resets certain values when changing data source."""
        self._ax = None
        self._values = None
        self._previous_values = None
        self.canvas.clear()

    def load_data(self, dfs: dict[str, polars.DataFrame]):
        """Loads data for plotting."""

        self._ax = self.figure.add_subplot(111)

        # Calculate hourly sums for each subject
        data = [(subject, df["studied_hours"].sum()) for subject, df in dfs.items()]

        if not data:
            return  # Nothing to plot

        labels, values = zip(*data, strict=False)
        total = sum(values)

        # Separate small slices (<1%) into "Other"
        main_labels = []
        main_values = []
        other_value = 0

        for label, value in zip(labels, values, strict=False):
            if value / total < 0.01:
                other_value += value
            else:
                main_labels.append(label)
                main_values.append(value)

        if other_value > 0:
            main_labels.append("Other")
            main_values.append(other_value)

        self._values = main_values

        # Create pie chart
        wedges, texts, autotexts = self._ax.pie(
            main_values,
            labels=main_labels,
            autopct=lambda pct: f"{pct:.1f}%" if pct >= 1 else "",
            wedgeprops=dict(width=0.4, edgecolor="w"),
            startangle=90,
            pctdistance=0.85,
            labeldistance=1.05,
        )

        # Create center text
        self._previous_total_hours = self._total_hours
        self._total_hours = sum(main_values)
        self._center_text = self._ax.text(
            0,
            0,
            "0.0h",
            ha="center",
            va="center",
            fontsize=20,
            fontweight="bold",
            color=self.colors["text"],
        )

        # Animation
        self._animation = FuncAnimation(
            self.figure,
            self.animate_center_text,
            frames=30,
            interval=1000 // 60,
            blit=True,
            repeat=False,
        )

        self._ax.set_facecolor(self.colors["background"])

        # Adjust label colors
        for text in texts + autotexts:
            text.set_color(self.colors["text"])
            text.set_fontsize(11)
            text.set_fontweight("bold")

        self.canvas.draw()

    def animate_center_text(self, i):
        frames = 30
        t = ease_in_out_quad(i / frames)
        delta = self._total_hours - self._previous_total_hours
        value = t * delta + self._previous_total_hours
        self._center_text.set_text(f"{value:.1f}h")
        return [self._center_text]
