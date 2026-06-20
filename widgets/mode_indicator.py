from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPainter, QColor, QFont

MODES = ["toggle", "push", "vad"]
_LABELS = ["T", "P", "A"]
_TOOLTIPS = {
    "toggle": "Toggle",
    "push": "Push-to-talk",
    "vad": "Voice Activity",
}


class ModeIndicator(QWidget):
    mode_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._mode = "toggle"
        self._blocked = False
        self.setFixedSize(18, 16)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(_TOOLTIPS[self._mode])

    def set_blocked(self, blocked):
        self._blocked = blocked

    def set_mode(self, mode):
        if mode in MODES:
            self._mode = mode
            self.setToolTip(_TOOLTIPS[mode])
            self.update()

    def mousePressEvent(self, event):
        if self._blocked:
            return
        if event.button() == Qt.MouseButton.LeftButton:
            idx = (MODES.index(self._mode) + 1) % len(MODES)
            self._mode = MODES[idx]
            self.setToolTip(_TOOLTIPS[self._mode])
            self.mode_changed.emit(self._mode)
            self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 0))

        idx = MODES.index(self._mode)
        font = QFont("Segoe UI", 7)
        painter.setFont(font)
        painter.setPen(QColor(80, 80, 80))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, _LABELS[idx])
