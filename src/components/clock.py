import datetime
import math

from PySide6.QtCore import QPoint, QPointF, QRectF, Qt, QTimer
from PySide6.QtGui import QFont, QPainter, QPainterPath, QPaintEvent, QPen, QPixmap
from PySide6.QtWidgets import QWidget
from styles.colors import Colors


class Clock(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Clock")

        self.__timer = QTimer(self)
        self.__timer.timeout.connect(self.repaint)
        self.__timer.start(1000 / 144)

        # Constants
        self.hand_second_length = 0.75
        self.hand_minute_length = 0.90
        self.hand_hour_length = 0.50

        self.hand_second_width = 0.010
        self.hand_minute_width = 0.025
        self.hand_hour_width = 0.035

        # Layers
        self.background = None
        self.foreground = None
        # Current clock hand
        self.hand_second = None
        self.hand_minute = None
        self.hand_hour = None
        # Start clock hand
        self.start_time = None
        self.hand_second_start = None
        self.hand_minute_start = None
        self.hand_hour_start = None
        # End clock hand
        self.stop_time = None
        self.hand_second_stop = None
        self.hand_minute_stop = None
        self.hand_hour_stop = None

        self.radius = 0.95 * (min(self.width(), self.height()) / 2)

        self.centerX = int(self.width() / 2)
        self.centerY = int(self.height() / 2)

        # Create pens
        self.pen_text = QPen(Colors.TEXT)
        self.pen_text.setWidth(2)
        self.pen_border_white = QPen("white")
        self.pen_border_white.setWidth(1)
        self.pen_border_black = QPen("black")
        self.pen_border_black.setWidth(2)
        self.pen_border = QPen("black")
        self.pen_border.setWidth(1)
        self.pen_arc_red = QPen("red")
        self.pen_arc_red.setWidth(3)
        self.pen_border_red = QPen("red")
        self.pen_border_red.setWidth(1)
        self.pen_blue = QPen("blue")
        self.pen_blue.setWidth(3)
        self.pen_border_blue = QPen("blue")
        self.pen_border_blue.setWidth(1)

        # Generate graphics
        self.resizeEvent(None)

    def __create_clock_hand(self, length: float, width: float) -> QPainterPath:
        """Returns a QPainterPath representing a clock hand."""
        path = QPainterPath()

        # Create a triangular hand pointing upwards
        path.moveTo(-width, -length)
        path.lineTo(width, -length)
        path.lineTo(width, 0)
        path.lineTo(-width, 0)
        path.closeSubpath()

        return path

    def __draw_rotated_hand(
        self, hand: QPainterPath, painter: QPainter, angle_degrees: float
    ) -> None:
        """Rotates the hand to the correct angle."""
        painter.save()
        painter.translate(QPoint(self.centerX, self.centerY))
        painter.rotate(angle_degrees)
        painter.drawPath(hand)
        painter.restore()

    def __create_background(self) -> QPixmap:
        """Returns QPixmap as background."""
        background = QPixmap(self.size())
        background.fill(Qt.transparent)

        painter = QPainter(background)
        painter.setOpacity(1.0)
        painter.setRenderHint(QPainter.Antialiasing)

        # Background circle
        self.radius = 0.95 * (min(self.width(), self.height()) / 2)

        self.centerX = int(self.width() / 2)
        self.centerY = int(self.height() / 2)

        painter.setBrush(Colors.PRIMARY)
        painter.drawEllipse(
            QPoint(self.centerX, self.centerY), self.radius, self.radius
        )

        angle = -math.pi / 2 + math.pi / 30
        hour = 1

        # Outer marks
        for _ in range(12 * 5):
            angle += math.pi / 30
            hour += 1

            painter.setPen(Colors.TEXT)
            painter.setBrush(Colors.TEXT)

            if hour % 5 == 0:
                painter.drawPolygon(
                    [
                        QPointF(
                            self.centerX + math.cos(angle - 0.01) * self.radius * 0.95,
                            self.centerY + math.sin(angle - 0.01) * self.radius * 0.95,
                        ),
                        QPointF(
                            self.centerX + math.cos(angle - 0.01) * self.radius * 0.85,
                            self.centerY + math.sin(angle - 0.01) * self.radius * 0.85,
                        ),
                        QPointF(
                            self.centerX + math.cos(angle + 0.01) * self.radius * 0.85,
                            self.centerY + math.sin(angle + 0.01) * self.radius * 0.85,
                        ),
                        QPointF(
                            self.centerX + math.cos(angle + 0.01) * self.radius * 0.95,
                            self.centerY + math.sin(angle + 0.01) * self.radius * 0.95,
                        ),
                    ]
                )
            else:
                painter.drawLine(
                    QPointF(
                        self.centerX + math.cos(angle) * self.radius * 0.875,
                        self.centerY + math.sin(angle) * self.radius * 0.875,
                    ),
                    QPointF(
                        self.centerX + math.cos(angle) * self.radius * 0.925,
                        self.centerY + math.sin(angle) * self.radius * 0.925,
                    ),
                )
        painter.end()
        return background

    def __create_foreground(self) -> QPixmap:
        """Returns QPixmap as foreground."""
        foreground = QPixmap(self.size())
        foreground.fill(Qt.transparent)

        painter = QPainter(foreground)
        painter.setBrush(Colors.TEXT)
        painter.setPen(self.pen_border_white)
        painter.setOpacity(1.0)
        painter.setRenderHint(QPainter.Antialiasing)

        r = self.radius * 0.050
        painter.drawEllipse(
            QPoint(self.centerX, self.centerY),
            r,
            r,
        )
        return foreground

    def __calculate_clock_hand_angles(
        self, time: datetime.datetime
    ) -> tuple[float, float, float]:
        """Returns clock hand angles based on time."""
        seconds = time.second + time.microsecond / 1000000
        minutes = time.minute
        hours = time.hour

        angle_second = (seconds / 60) * 360
        angle_minute = (minutes / 60) * 360 + angle_second / 60
        angle_hour = (hours % 12 + minutes / 60 + seconds / 3600) * 30

        return angle_second, angle_minute, angle_hour

    def __calculate_span_angles(
        self, start_angle: float, end_angle: float
    ) -> tuple[float, float]:
        """Calculates the span and middle angle between start and end."""
        start_angle -= 90
        end_angle -= 90
        span_angle = (end_angle - start_angle) % 360
        span_mid_angle = (start_angle + span_angle / 2) % 360

        return span_angle, span_mid_angle

    def __draw_arc(
        self,
        painter: QPainter,
        length: float,
        start_angle: float,
        span_angle: float,
    ) -> None:
        """Paints an arc between 2 angles."""
        rect = QRectF(
            self.centerX - length,
            self.centerY - length,
            length * 2,
            length * 2,
        )
        painter.drawArc(rect, int((-start_angle + 90) * 16), int(-span_angle * 16))

    def __draw_arc_text(
        self,
        painter: QPainter,
        fill_color: str,
        length: float,
        mid_angle: float,
        text: str,
    ) -> None:
        """Paints the numeric text on arc."""
        mid_angle_rad = math.radians(mid_angle)
        font = QFont("Arial", self.radius // 10)

        # Position text
        text_radius = length * 0.90
        text_x = (
            self.centerX + math.cos(mid_angle_rad) * text_radius - text_radius * 0.05
        )
        text_y = (
            self.centerY + math.sin(mid_angle_rad) * text_radius + text_radius * 0.05
        )
        path = QPainterPath()
        path.addText(text_x, text_y, font, text)

        # Outline
        painter.setPen(self.pen_border_black)
        painter.drawPath(path)

        # Fill
        painter.setPen(fill_color)
        painter.setBrush(fill_color)
        painter.drawPath(path)

    def set_start_time(self, time: datetime.datetime):
        """Set start time."""
        self.start_time = time

    def set_stop_time(self, time: datetime.datetime):
        """Set stop time."""
        self.stop_time = time

    def reset_times(self):
        """Clears time."""
        self.start_time = None
        self.stop_time = None

    def resizeEvent(self, event):
        """Resize items."""
        self.background = self.__create_background()
        self.foreground = self.__create_foreground()
        # Current time hands
        self.hand_second = self.__create_clock_hand(
            self.radius * self.hand_second_length, self.radius * self.hand_second_width
        )
        self.hand_minute = self.__create_clock_hand(
            self.radius * self.hand_minute_length, self.radius * self.hand_minute_width
        )
        self.hand_hour = self.__create_clock_hand(
            self.radius * self.hand_hour_length, self.radius * self.hand_hour_width
        )
        # Start time hands
        self.hand_second_start = self.__create_clock_hand(
            self.radius * self.hand_second_length, self.radius * self.hand_second_width
        )
        self.hand_minute_start = self.__create_clock_hand(
            self.radius * self.hand_minute_length, self.radius * self.hand_minute_width
        )
        self.hand_hour_start = self.__create_clock_hand(
            self.radius * self.hand_hour_length, self.radius * self.hand_hour_width
        )
        # End time hands
        self.hand_second_stop = self.__create_clock_hand(
            self.radius * self.hand_second_length, self.radius * self.hand_second_width
        )
        self.hand_minute_stop = self.__create_clock_hand(
            self.radius * self.hand_minute_length, self.radius * self.hand_minute_width
        )
        self.hand_hour_stop = self.__create_clock_hand(
            self.radius * self.hand_hour_length, self.radius * self.hand_hour_width
        )
        super().resizeEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Draws clock animation."""
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setBrush(Colors.TEXT)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.drawPixmap(0, 0, self.background)
        painter.setOpacity(1.0)

        now = datetime.datetime.now()
        angle_second, angle_minute, angle_hour = self.__calculate_clock_hand_angles(now)

        # Start clock hands
        if self.start_time is not None:
            painter.setBrush("red")
            painter.setPen(self.pen_border_red)

            angle_second_start, angle_minute_start, angle_hour_start = (
                self.__calculate_clock_hand_angles(self.start_time)
            )
            self.__draw_rotated_hand(self.hand_hour_start, painter, angle_hour_start)
            self.__draw_rotated_hand(
                self.hand_minute_start, painter, angle_minute_start
            )
            self.__draw_rotated_hand(
                self.hand_second_start, painter, angle_second_start
            )
            # Calculate values
            painter.setPen(self.pen_arc_red)
            delta = now - self.start_time
            second = int(round(delta.total_seconds() % 60, 0))
            minute = int(delta.total_seconds() // 60)
            hour = int(delta.total_seconds() // 3600)

            # Calculate span and middle
            angle_span_second, middle_angle_second = self.__calculate_span_angles(
                angle_second_start, angle_second
            )
            angle_span_minute, middle_angle_minute = self.__calculate_span_angles(
                angle_minute_start, angle_minute
            )
            angle_span_hour, middle_angle_hour = self.__calculate_span_angles(
                angle_hour_start, angle_hour
            )

            # Draw arcs
            self.__draw_arc(
                painter,
                self.radius * self.hand_second_length,
                angle_second_start,
                angle_span_second,
            )
            self.__draw_arc(
                painter,
                self.radius * self.hand_minute_length,
                angle_minute_start,
                angle_span_minute,
            )
            self.__draw_arc(
                painter,
                self.radius * self.hand_hour_length,
                angle_hour_start,
                angle_span_hour,
            )

            # Draw text
            self.__draw_arc_text(
                painter,
                "red",
                self.radius * self.hand_second_length,
                middle_angle_second,
                str(second),
            )
            self.__draw_arc_text(
                painter,
                "red",
                self.radius * self.hand_minute_length,
                middle_angle_minute,
                str(minute),
            )
            self.__draw_arc_text(
                painter,
                "red",
                self.radius * self.hand_hour_length,
                middle_angle_hour,
                str(hour),
            )

        # End clock hands
        if self.stop_time is not None:
            painter.setBrush("blue")
            angle_second_stop, angle_minute_stop, angle_hour_stop = (
                self.__calculate_clock_hand_angles(self.stop_time)
            )
            self.__draw_rotated_hand(self.hand_hour_stop, painter, angle_hour_stop)
            self.__draw_rotated_hand(self.hand_minute_stop, painter, angle_minute_stop)
            self.__draw_rotated_hand(self.hand_second_stop, painter, angle_second_stop)
            # Draw arc
            painter.setPen(self.pen_blue)
            painter.setPen(self.pen_border)

        # Current clock hands
        painter.setBrush(Colors.TEXT)
        painter.setPen(self.pen_border_white)
        painter.setOpacity(1.0)

        self.__draw_rotated_hand(self.hand_hour, painter, angle_hour)
        self.__draw_rotated_hand(self.hand_minute, painter, angle_minute)
        self.__draw_rotated_hand(self.hand_second, painter, angle_second)

        # Draw foreground
        painter.setOpacity(1.0)
        painter.drawPixmap(0, 0, self.foreground)
        painter.end()
