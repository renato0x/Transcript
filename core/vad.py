import webrtcvad
import numpy as np
from PySide6.QtCore import QObject, Signal


class VAD(QObject):
    silence_detected = Signal()

    def __init__(self, sample_rate=16000, silence_ms=1000):
        super().__init__()
        self.vad = webrtcvad.Vad()
        self.vad.set_mode(1)
        self.sample_rate = sample_rate
        self.frame_size = int(sample_rate * 0.03)
        self.silence_frames = int(silence_ms / 30)
        self._buffer = b""
        self._silence_count = 0
        self._running = False

    def start(self):
        self._buffer = b""
        self._silence_count = 0
        self._running = True

    def stop(self):
        self._running = False
        self._buffer = b""
        self._silence_count = 0

    def process(self, chunk):
        if not self._running:
            return
        raw = (chunk * 32767).astype(np.int16).tobytes()
        self._buffer += raw
        while len(self._buffer) >= self.frame_size * 2:
            frame = self._buffer[: self.frame_size * 2]
            self._buffer = self._buffer[self.frame_size * 2 :]
            try:
                speech = self.vad.is_speech(frame, self.sample_rate)
            except Exception:
                speech = True
            if speech:
                self._silence_count = 0
            else:
                self._silence_count += 1
                if self._silence_count >= self.silence_frames:
                    self._running = False
                    self.silence_detected.emit()
                    return
