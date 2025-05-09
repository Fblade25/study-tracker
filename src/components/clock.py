import datetime
import math

from PySide6.QtCore import QPoint, QPointF, Qt, QTimer
from PySide6.QtGui import QColor, QPainter, QPaintEvent, QPen, QPixmap
from PySide6.QtWidgets import QWidget
from styles.colors import Colors


class Clock(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Clock")

        self.__timer = QTimer(self)
        self.__timer.timeout.connect(self.repaint)
        self.__timer.start(1)

        self.background = None
        self.resizeEvent(None)

        self.radius = 0.95 * (min(self.width(), self.height()) / 2)

        self.centerX = int(self.width() / 2)
        self.centerY = int(self.height() / 2)

    def resizeEvent(self, event):
        """Redraws background of clock."""
        self.background = QPixmap(self.size())
        self.background.fill(Qt.transparent)

        painter = QPainter(self.background)
        painter.setRenderHint(QPainter.Antialiasing)

        self.radius = 0.95 * (min(self.width(), self.height()) / 2)

        self.centerX = int(self.width() / 2)
        self.centerY = int(self.height() / 2)

        painter.setBrush(Colors.PRIMARY)
        painter.drawEllipse(
            QPoint(self.centerX, self.centerY), self.radius, self.radius
        )

        angle = -math.pi / 2 + math.pi / 30
        hour = 1

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

    def paintEvent(self, event: QPaintEvent) -> None:
        """Draws clock animation."""
        super().paintEvent(event)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        if self.background:
            painter.drawPixmap(0, 0, self.background)

        now = datetime.datetime.now().time()

        seconds = (now.second * 1000000 + now.microsecond) / 1000000

        painter.setPen(QPen(QColor(255, 255, 255, int(256 * 0.6)), 3))
        angle = -math.pi / 2 + seconds * math.pi / 30
        destX = math.cos(angle) * self.radius * 0.95
        destY = math.sin(angle) * self.radius * 0.95
        painter.drawLine(
            self.centerX,
            self.centerY,
            int(self.centerX + destX),
            int(self.centerY + destY),
        )

        painter.setPen(QColor(255, 255, 255))
        painter.setBrush(QColor(255, 255, 255, 150))

        minuteAngle = math.pi * 2 * (now.minute / 60 + now.second / 3600)
        minuteAngle = -(math.pi / 2 - minuteAngle)

        painter.drawPolygon(
            [
                QPointF(
                    self.centerX + math.cos(minuteAngle) * self.radius * 0.93,
                    self.centerY + math.sin(minuteAngle) * self.radius * 0.93,
                ),
                QPointF(
                    self.centerX + math.cos(minuteAngle - 0.4) * self.radius * 0.1,
                    self.centerY + math.sin(minuteAngle - 0.4) * self.radius * 0.1,
                ),
                QPointF(
                    self.centerX + math.cos(minuteAngle + 0.4) * self.radius * 0.1,
                    self.centerY + math.sin(minuteAngle + 0.4) * self.radius * 0.1,
                ),
            ]
        )

        hourAngle = math.pi * 2 * ((now.hour % 12 + now.minute / 60) / 12)
        hourAngle = -(math.pi / 2 - hourAngle)

        painter.drawPolygon(
            [
                QPointF(
                    self.centerX + math.cos(hourAngle) * self.radius * 0.6,
                    self.centerY + math.sin(hourAngle) * self.radius * 0.6,
                ),
                QPointF(
                    self.centerX + math.cos(hourAngle - 0.3) * self.radius * 0.1,
                    self.centerY + math.sin(hourAngle - 0.3) * self.radius * 0.1,
                ),
                QPointF(
                    self.centerX + math.cos(hourAngle + 0.3) * self.radius * 0.1,
                    self.centerY + math.sin(hourAngle + 0.3) * self.radius * 0.1,
                ),
            ]
        )

        painter.end()
