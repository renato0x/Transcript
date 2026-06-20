from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Signal, QPointF
from PySide6.QtGui import QPainter, QColor


class MuteWidget(QWidget):
    muted_changed = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._muted = False
        self.setFixedSize(16, 16)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

    def is_muted(self):
        return self._muted

    def set_muted(self, muted):
        if self._muted != muted:
            self._muted = muted
            self.muted_changed.emit(self._muted)
            self.update()

    def toggle(self):
        self.set_muted(not self._muted)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.toggle()
            event.accept()
        else:
            super().mousePressEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 0))

        cx = self.width() / 2.0
        cy = self.height() / 2.0

        if self._muted:
            color = QColor(80, 80, 80)
            line_color = QColor(120, 80, 80)
        else:
            color = QColor(150, 150, 150)
            line_color = QColor(60, 60, 60)

        speaker = [(-4, 3), (0, 3), (4, -1), (4, 5), (0, 1), (-4, 1)]
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(color)
        body = [QPointF(cx + x, cy + y) for x, y in speaker]
        painter.drawPolygon(body)

        if self._muted:
            painter.setPen(QColor(180, 80, 80))
            painter.drawLine(int(cx + 5), int(cy - 4), int(cx + 8), int(cy + 4))
            painter.drawLine(int(cx + 5), int(cy + 4), int(cx + 8), int(cy - 4))
