from collections import deque
import math
import threading
import numpy as np
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QPainterPath, QColor, QPen


class WaveformWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._buffer = deque(maxlen=4096)
        self._lock = threading.Lock()
        self._recording = False
        self._transcribing = False
        self._decay = 0.0
        self._fade_in = 0.0
        self._pulse = 0.0
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(16)
        self.setMinimumHeight(40)

    def set_recording(self, recording):
        self._recording = recording
        if recording:
            with self._lock:
                self._buffer.clear()
            self._decay = 0.0
            self._fade_in = 0.0
        else:
            self._decay = 1.5

    def set_transcribing(self, transcribing):
        self._transcribing = transcribing
        if transcribing:
            self._pulse = 0.0

    def add_samples(self, samples):
        with self._lock:
            self._buffer.extend(samples)

    def _tick(self):
        if self._recording and self._fade_in < 1.0:
            self._fade_in = min(1.0, self._fade_in + 0.04)
        if self._decay > 0:
            self._decay -= 0.016
            if self._decay <= 0:
                self._decay = 0.0
                if not self._recording:
                    with self._lock:
                        self._buffer.clear()
        self._pulse += 0.06
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = self.width()
        h = self.height()
        center_y = h / 2.0

        painter.fillRect(self.rect(), QColor("#000000"))

        painter.setPen(QPen(QColor(25, 25, 25), 0.5))
        painter.drawLine(0, center_y, w, center_y)

        has_data = False
        normalized = None
        with self._lock:
            if self._buffer and len(self._buffer) >= 2:
                data = list(self._buffer)
                arr = np.array(data, dtype=np.float32)
                max_val = float(np.max(np.abs(arr)))
                if max_val >= 0.001:
                    normalized = arr / max_val
                    has_data = True

        gain = 1.0
        idle_blend = 0.0

        if self._recording and self._fade_in < 1.0:
            idle_blend = 1.0 - self._fade_in
            gain = self._fade_in
        elif not self._recording and self._decay > 0:
            t = self._decay / 1.5
            gain = t ** 1.5
            idle_blend = 1.0 - t ** 0.8

        if has_data and gain > 0.01:
            n = len(normalized)
            max_points = w * 2
            if n > max_points:
                step = n // max_points
                normalized = normalized[::step]
                n = len(normalized)

            amp_scale = (h * 0.4) * gain
            step_x = w / max(n - 1, 1)

            path = QPainterPath()
            path.moveTo(0.0, center_y - float(normalized[0]) * amp_scale)

            for i in range(1, n - 1):
                x = i * step_x
                y = center_y - float(normalized[i]) * amp_scale
                mid_x = ((i + 1) * step_x + x) / 2
                mid_y = (center_y - float(normalized[i + 1]) * amp_scale + y) / 2
                path.quadTo(x, y, mid_x, mid_y)

            xn = (n - 1) * step_x
            yn = center_y - float(normalized[-1]) * amp_scale
            path.lineTo(xn, yn)

            painter.setOpacity(gain)
            painter.setPen(QPen(QColor(150, 150, 150), 0.8))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawPath(path)
            painter.setOpacity(1.0)

        if idle_blend > 0.01:
            self._draw_fluid(painter, w, h, center_y, idle_blend)
        elif not has_data:
            self._draw_fluid(painter, w, h, center_y, 1.0)

    def _draw_fluid(self, painter, w, h, center_y, alpha):
        bright = self._transcribing
        amp = (math.sin(self._pulse) * 0.5 + 0.5) * 0.4 + 0.15
        if bright:
            amp = amp * 0.7 + 0.3
        n_points = 40
        path = QPainterPath()
        step_x = w / (n_points - 1)
        path.moveTo(0.0, center_y)
        for i in range(n_points):
            x = i * step_x
            y = center_y - math.sin(i * 0.35 + self._pulse * 0.8) * (h * 0.12) * amp
            path.lineTo(x, y)

        base = 100 if not bright else 160
        a = int(base * alpha)
        painter.setOpacity(alpha)
        painter.setPen(QPen(QColor(110, 110, 110, a), 0.7))
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(path)
