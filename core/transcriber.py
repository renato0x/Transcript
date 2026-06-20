import threading
from PySide6.QtCore import QObject, Signal
from faster_whisper import WhisperModel


class Transcriber(QObject):
    finished = Signal(str)
    error = Signal(str)
    loading = Signal()
    started = Signal()

    def __init__(self, model_size="small", device="cpu"):
        super().__init__()
        self.model_size = model_size
        self.device = device
        self._model = None
        self._busy = False

    @property
    def busy(self):
        return self._busy

    @property
    def model_loaded(self):
        return self._model is not None

    def transcribe(self, audio):
        if self._busy:
            return
        self._busy = True

        if self._model is None:
            self.loading.emit()

        def _run():
            try:
                if self._model is None:
                    self._model = WhisperModel(
                        self.model_size,
                        device=self.device,
                        compute_type="int8",
                    )
                self.started.emit()
                segments, _ = self._model.transcribe(audio, beam_size=5, language="pt")
                text = " ".join(seg.text for seg in segments)
                self._busy = False
                self.finished.emit(text.strip())
            except Exception as e:
                self._busy = False
                self.error.emit(str(e))

        threading.Thread(target=_run, daemon=True).start()

    def unload(self):
        self._model = None
