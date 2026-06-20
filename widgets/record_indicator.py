from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer, QPointF
from PySide6.QtGui import QPainter, QColor


class RecordIndicator(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._state = "idle"
        self._size = 3.5
        self._glow = 5.0
        self._direction = 1
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(50)
        self.setFixedSize(20, 20)

    def set_state(self, state):
        self._state = state
        self._size = 3.5
        self._glow = 5.0
        self._direction = 1
        self.update()

    def _tick(self):
        pulse = self._state in ("recording", "transcribing", "loading")
        if pulse:
            speed = 0.4 if self._state == "loading" else 1.0
            self._size += 0.08 * self._direction * speed
            self._glow += 0.15 * self._direction * speed
            if self._size >= 5.5:
                self._size = 5.5
                self._glow = 7.0
                self._direction = -1
            elif self._size <= 3.0:
                self._size = 3.0
                self._glow = 4.5
                self._direction = 1
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 0))

        cx = self.width() / 2.0
        cy = self.height() / 2.0

        if self._state == "recording":
            color = QColor(255, 50, 50)
            glow_color = QColor(255, 50, 50, 35)
        elif self._state == "loading":
            color = QColor(90, 90, 90)
            glow_color = QColor(90, 90, 90, 25)
        elif self._state == "transcribing":
            color = QColor(200, 180, 60)
            glow_color = QColor(200, 180, 60, 35)
        else:
            color = QColor(55, 55, 55)
            glow_color = QColor(55, 55, 55, 15)

        painter.setBrush(glow_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(cx, cy), self._glow, self._glow)

        painter.setBrush(color)
        painter.drawEllipse(QPointF(cx, cy), self._size, self._size)
