from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Signal, QPointF
from PySide6.QtGui import QPainter, QColor, QPen


class MuteWidget(QWidget):
    muted_changed = Signal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._muted = False
        self._hovered = False
        self.setFixedSize(20, 20)
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
            body_color = QColor(80, 70, 70)
            arc_color = QColor(80, 60, 60)
            cross_color = QColor(200, 80, 80)
        else:
            body_color = QColor(160, 160, 160)
            arc_color = QColor(120, 120, 120)
            cross_color = QColor(0, 0, 0)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(body_color)

        speaker_body = [QPointF(cx - 5, cy - 3), QPointF(cx - 1, cy - 3),
                        QPointF(cx + 3, cy - 6), QPointF(cx + 3, cy + 6),
                        QPointF(cx - 1, cy + 3), QPointF(cx - 5, cy + 3)]
        painter.drawPolygon(speaker_body)

        painter.setPen(QPen(arc_color, 1.5))
        painter.setBrush(Qt.BrushStyle.NoBrush)

        if not self._muted:
            painter.drawArc(int(cx + 4), int(cy - 7), 6, 14, -45 * 16, 90 * 16)
            painter.drawArc(int(cx + 7), int(cy - 7), 6, 14, -45 * 16, 90 * 16)

        if self._muted:
            painter.setPen(QPen(cross_color, 2))
            painter.drawLine(int(cx + 4), int(cy - 5), int(cx + 8), int(cy + 5))
            painter.drawLine(int(cx + 4), int(cy + 5), int(cx + 8), int(cy - 5))

        if self._hovered:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(255, 255, 255, 12))
            painter.drawRoundedRect(self.rect(), 3, 3)
