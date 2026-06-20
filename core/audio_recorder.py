import numpy as np
import sounddevice as sd
from PySide6.QtCore import QObject, Signal


def _find_input_device():
    devices = sd.query_devices()
    for i, dev in enumerate(devices):
        if dev["max_input_channels"] > 0 and dev["hostapi"] == 0:
            return i
    for i, dev in enumerate(devices):
        if dev["max_input_channels"] > 0:
            return i
    return None


class AudioRecorder(QObject):
    chunk_ready = Signal(np.ndarray)

    def __init__(self, samplerate=16000, blocksize=1024):
        super().__init__()
        self.samplerate = samplerate
        self.blocksize = blocksize
        self._recording = False
        self._stream = None
        self._buffer = []

    @property
    def recording(self):
        return self._recording

    def start(self):
        if self._recording:
            return
        self._recording = True
        self._buffer = []

        device = _find_input_device()

        def callback(indata, frames, time, status):
            if status:
                print(f"Audio error: {status}")
            chunk = indata[:, 0].copy()
            self._buffer.append(chunk)
            self.chunk_ready.emit(chunk)

        self._stream = sd.InputStream(
            samplerate=self.samplerate,
            channels=1,
            blocksize=self.blocksize,
            dtype="float32",
            device=device,
            callback=callback,
        )
        self._stream.start()

    def stop(self):
        if not self._recording:
            return None
        self._recording = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        if self._buffer:
            return np.concatenate(self._buffer)
        return None
