from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Signal, QPointF
from PySide6.QtGui import QPainter, QColor, QPen


class MuteWidget(QWidget):
    muted_changed = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._muted = False
        self._hovered = False
        self.setFixedSize(16, 16)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMouseTracking(True)

    def is_muted(self):
        return self._muted

    def set_muted(self, muted):
        if self._muted != muted:
            self._muted = muted
            self.muted_changed.emit(self._muted)
            self.update()

    def toggle(self):
        self.set_muted(not self._muted)

    def enterEvent(self, event):
        self._hovered = True
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self._hovered = False
        self.update()
        super().leaveEvent(event)

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
            body_color = QColor(60, 58, 58)
            cross_color = QColor(160, 70, 70)
        else:
            body_color = QColor(80, 80, 80)
            arc_color = QColor(80, 80, 80)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(body_color)

        speaker_body = [QPointF(cx - 4, cy - 2), QPointF(cx - 1, cy - 2),
                        QPointF(cx + 2, cy - 5), QPointF(cx + 2, cy + 5),
                        QPointF(cx - 1, cy + 2), QPointF(cx - 4, cy + 2)]
        painter.drawPolygon(speaker_body)

        if not self._muted:
            painter.setPen(QPen(arc_color, 1.2))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawArc(int(cx + 3), int(cy - 5), 4, 10, -45 * 16, 90 * 16)
            painter.drawArc(int(cx + 6), int(cy - 5), 4, 10, -45 * 16, 90 * 16)

        if self._muted:
            painter.setPen(QPen(cross_color, 1.5))
            painter.drawLine(int(cx + 3), int(cy - 4), int(cx + 7), int(cy + 4))
            painter.drawLine(int(cx + 3), int(cy + 4), int(cx + 7), int(cy - 4))

        if self._hovered:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(255, 255, 255, 10))
            painter.drawRoundedRect(self.rect(), 2, 2)
