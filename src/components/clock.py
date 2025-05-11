import datetime
import math

from PySide6.QtCore import QPoint, QPointF, Qt, QTimer
from PySide6.QtGui import (
    QPainter,
    QPainterPath,
    QPaintEvent,
    QPixmap,
)
from PySide6.QtWidgets import QWidget
from styles.colors import Colors


class Clock(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Clock")

        self.__timer = QTimer(self)
        self.__timer.timeout.connect(self.repaint)
        self.__timer.start(1000 / 144)

        self.background = None
        self.hand_second = None
        self.hand_minute = None
        self.hand_hour = None
        self.resizeEvent(None)

        self.radius = 0.95 * (min(self.width(), self.height()) / 2)

        self.centerX = int(self.width() / 2)
        self.centerY = int(self.height() / 2)

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
        r = self.radius * 0.035

        # Middle circle
        painter.drawEllipse(
            QPoint(self.centerX, self.centerY),
            r,
            r,
        )
        painter.end()
        return background

    def __calculate_clock_hand_angles(
        self, seconds: float, minutes: int, hours: int
    ) -> tuple[float, float, float]:
        """Returns clock hand angles based on time."""
        angle_second = (seconds / 60) * 360
        angle_minute = (minutes / 60) * 360 + angle_second / 60
        angle_hour = (hours / 12) * 360 + angle_minute / 60

        return angle_second, angle_minute, angle_hour

    def resizeEvent(self, event):
        """Resize items."""
        self.background = self.__create_background()
        self.hand_second = self.__create_clock_hand(
            self.radius * 0.90, self.radius * 0.005
        )
        self.hand_minute = self.__create_clock_hand(
            self.radius * 0.70, self.radius * 0.010
        )
        self.hand_hour = self.__create_clock_hand(
            self.radius * 0.45, self.radius * 0.020
        )
        super().resizeEvent(event)

    def paintEvent(self, event: QPaintEvent) -> None:
        """Draws clock animation."""
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setBrush(Colors.TEXT)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.drawPixmap(0, 0, self.background)

        # Rotate hands based on time
        now = datetime.datetime.now()

        seconds = now.second + now.microsecond / 1000000
        minutes = now.minute
        hours = now.hour

        angle_second, angle_minute, angle_hour = self.__calculate_clock_hand_angles(
            seconds, minutes, hours
        )

        self.__draw_rotated_hand(self.hand_second, painter, angle_second)
        self.__draw_rotated_hand(self.hand_minute, painter, angle_minute)
        self.__draw_rotated_hand(self.hand_hour, painter, angle_hour)

        painter.end()
