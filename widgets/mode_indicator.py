from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, Signal, QTimer, QPointF
from PySide6.QtGui import QPainter, QPainterPath, QColor, QFont, QPen

MODES = ["toggle", "push", "vad", "ideas"]
_LABELS = ["T", "P", "A", ""]
_TOOLTIPS = {
    "toggle": "Toggle",
    "push": "Push-to-talk",
    "vad": "Voice Activity",
    "ideas": "Ideias",
}


class ModeIndicator(QWidget):
    mode_changed = Signal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._mode = "toggle"
        self._blocked = False
        self._pulse = 0.0
        self._direction = 1
        self.setFixedSize(22, 20)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setToolTip(_TOOLTIPS[self._mode])

        self._pulse_timer = QTimer(self)
        self._pulse_timer.timeout.connect(self._tick_pulse)
        self._pulse_timer.start(40)

    def _tick_pulse(self):
        if self._mode == "ideas":
            self._pulse += 0.06 * self._direction
            if self._pulse >= 1.0:
                self._pulse = 1.0
                self._direction = -1
            elif self._pulse <= 0.0:
                self._pulse = 0.0
                self._direction = 1
            self.update()
        else:
            if self._pulse != 0.0:
                self._pulse = 0.0
                self.update()

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

        if self._mode == "ideas":
            self._draw_lightbulb(painter)
        else:
            idx = MODES.index(self._mode)
            font = QFont("Segoe UI", 7)
            painter.setFont(font)
            painter.setPen(QColor(80, 80, 80))
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, _LABELS[idx])

    def _draw_lightbulb(self, painter):
        cx = self.width() / 2.0
        cy = self.height() / 2.0 - 1

        pulse = self._pulse
        base_alpha = 160 + int(95 * pulse)
        glow = 2.5 + 2.0 * pulse

        bulb_color = QColor(255, 200, 50, base_alpha)
        glow_color = QColor(255, 200, 50, int(30 * (0.3 + 0.7 * pulse)))
        filament_color = QColor(255, 220, 100, base_alpha)
        base_color = QColor(100 + int(40 * pulse), 100 + int(40 * pulse), 100 + int(40 * pulse))

        painter.setBrush(glow_color)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(cx, cy - 2), glow * 1.8, glow * 1.6)

        bulb = QPainterPath()
        bulb.addEllipse(QPointF(cx, cy - 3), 5.0, 5.0)
        painter.setBrush(bulb_color)
        painter.setPen(QPen(QColor(220, 180, 40, base_alpha), 0.8))
        painter.drawPath(bulb)

        filament = QPainterPath()
        filament.moveTo(cx - 2.5, cy - 5)
        filament.lineTo(cx - 1.0, cy - 2)
        filament.lineTo(cx + 1.0, cy - 2)
        filament.lineTo(cx + 2.5, cy - 5)
        painter.setPen(QPen(filament_color, 0.8))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(filament)

        base = QPainterPath()
        base.moveTo(cx - 3.0, cy + 2.5)
        base.lineTo(cx + 3.0, cy + 2.5)
        base.lineTo(cx + 2.5, cy + 5.5)
        base.lineTo(cx - 2.5, cy + 5.5)
        base.closeSubpath()
        painter.setBrush(base_color)
        painter.setPen(QPen(QColor(70, 70, 70), 0.5))
        painter.drawPath(base)
