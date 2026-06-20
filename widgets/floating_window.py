import ctypes
import webbrowser

from PySide6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QMenu, QApplication, QPushButton,
    QMessageBox,
)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPainter, QPainterPath, QColor, QPen, QAction

from .waveform_widget import WaveformWidget
from .record_indicator import RecordIndicator
from .mode_indicator import ModeIndicator, MODES
from core.audio_recorder import AudioRecorder
from core.transcriber import Transcriber
from core.vad import VAD
from core import config as cfg
from notifier import show_notification
from autopaste import auto_paste
from version import VERSION
import sounds

_MODIFIER_VK = {
    "ctrl": 0x11, "alt": 0x12, "shift": 0x10,
}


def _parse_hotkey(hotkey_str):
    codes = []
    for p in hotkey_str.lower().split("+"):
        if p in _MODIFIER_VK:
            codes.append(_MODIFIER_VK[p])
        elif len(p) == 1:
            codes.append(ord(p.upper()))
    return codes


class FloatingWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setMouseTracking(True)

        self._config = cfg.load()
        self._drag_pos = None
        self._recording = False
        self._transcribing = False
        self._hovered = False
        self._flash = 0.0
        self._fade_opacity = 0.0
        self._update_url = ""

        self.indicator = RecordIndicator()
        self.mode_indicator = ModeIndicator()
        self.mode_indicator.set_mode(self._config.get("mode", "toggle"))
        self.mode_indicator.mode_changed.connect(self._on_mode_changed)
        self.waveform = WaveformWidget()
        self.close_btn = QPushButton("×")
        self.close_btn.setFixedSize(18, 18)
        self.close_btn.setFlat(True)
        self.close_btn.setStyleSheet("""
            QPushButton {
                color: #505050;
                font-size: 14px;
                border: none;
                background: transparent;
                padding: 0;
            }
            QPushButton:hover {
                color: #ffffff;
                background: rgba(255, 255, 255, 8);
                border-radius: 2px;
            }
        """)
        self.close_btn.clicked.connect(QApplication.instance().quit)

        container = QWidget(self)
        container.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        left_vbox = QVBoxLayout()
        left_vbox.setContentsMargins(0, 0, 0, 0)
        left_vbox.setSpacing(2)
        left_vbox.addStretch()
        left_vbox.addWidget(self.indicator)
        left_vbox.addWidget(self.mode_indicator)
        left_vbox.addStretch()

        layout = QHBoxLayout(container)
        layout.setContentsMargins(14, 10, 10, 10)
        layout.setSpacing(6)
        layout.addLayout(left_vbox)
        layout.addWidget(self.waveform, 1)
        layout.addWidget(self.close_btn)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(container)

        self.resize(270, 85)

        self.recorder = AudioRecorder()
        self.recorder.chunk_ready.connect(self._on_chunk)

        self.transcriber = Transcriber()
        self.transcriber.finished.connect(self._on_transcribed)
        self.transcriber.error.connect(self._on_error)
        self.transcriber.loading.connect(self._on_model_loading)
        self.transcriber.started.connect(self._on_transcribe_started)

        self.vad = VAD(silence_ms=self._config.get("vad_silence_ms", 1000))
        self.vad.silence_detected.connect(self._on_vad_silence)

        self._push_timer = QTimer(self)
        self._push_timer.timeout.connect(self._poll_push)
        self._push_vk_codes = []

        self._flash_timer = QTimer(self)
        self._flash_timer.timeout.connect(self._tick_flash)

        self._fade_timer = QTimer(self)
        self._fade_timer.timeout.connect(self._tick_fade)

        screen = QApplication.primaryScreen().geometry()
        self.move(
            screen.width() // 2 - self.width() // 2,
            screen.height() - self.height() - 60,
        )

        self.setWindowOpacity(0.0)
        QTimer.singleShot(50, self._start_fade)

    def _start_fade(self):
        self._fade_opacity = 0.0
        self._fade_timer.start(16)

    def _tick_fade(self):
        self._fade_opacity = min(1.0, self._fade_opacity + 0.08)
        self.setWindowOpacity(self._fade_opacity)
        if self._fade_opacity >= 1.0:
            self._fade_timer.stop()

    def _tick_flash(self):
        self._flash -= 0.04
        self.update()
        if self._flash <= 0.0:
            self._flash = 0.0
            self._flash_timer.stop()

    def _on_chunk(self, chunk):
        self.waveform.add_samples(chunk)
        if self._config.get("mode") == "vad" and self._recording:
            self.vad.process(chunk)

    def _on_mode_changed(self, mode):
        self._config["mode"] = mode
        cfg.save(self._config)

    @property
    def mode(self):
        return self._config.get("mode", "toggle")

    def closeEvent(self, event):
        self.recorder.stop()
        self.transcriber.unload()
        event.accept()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = self.rect().adjusted(1, 1, -1, -1)
        path = QPainterPath()
        path.addRoundedRect(rect, 10, 10)
        painter.fillPath(path, QColor("#0a0a0a"))

        border_color = QColor("#3a3a3a") if self._hovered else QColor("#1e1e1e")
        painter.setPen(QPen(border_color, 1))
        painter.drawPath(path)

        if self._flash > 0.01:
            flash_path = QPainterPath()
            flash_path.addRoundedRect(rect, 10, 10)
            flash_alpha = int(25 * self._flash)
            painter.fillPath(flash_path, QColor(255, 255, 255, flash_alpha))

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
            self._drag_pos = event.globalPosition().toPoint()
            event.accept()
        elif event.button() == Qt.MouseButton.RightButton:
            self._show_context_menu(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton and self._drag_pos:
            delta = event.globalPosition().toPoint() - self._drag_pos
            self.move(self.pos() + delta)
            self._drag_pos = event.globalPosition().toPoint()
            event.accept()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = None
            event.accept()

    def _show_context_menu(self, pos):
        menu = QMenu(self)
        menu.setStyleSheet(
            """
            QMenu {
                background-color: #1a1a1a;
                border: 1px solid #333333;
                color: #cccccc;
                padding: 4px;
            }
            QMenu::item:selected {
                background-color: #333333;
            }
        """
        )

        action_update = QAction("Check for Updates", self)
        action_update.triggered.connect(self._check_update_now)
        menu.addAction(action_update)

        action_about = QAction("About", self)
        action_about.triggered.connect(self._show_about)
        menu.addAction(action_about)

        menu.addSeparator()
        action_quit = QAction("Quit", self)
        action_quit.triggered.connect(QApplication.instance().quit)
        menu.addAction(action_quit)

        menu.exec(pos)

    def _show_about(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("About Transcript")
        msg.setText(f"Transcript v{VERSION}")
        msg.setInformativeText("Local speech transcription.\n\nrenato0x")
        msg.exec()

    def _check_update_now(self):
        from core.updater import UpdateChecker
        checker = UpdateChecker()
        checker.found.connect(lambda v, u: self.show_update_notification(v, u))
        import threading
        threading.Thread(target=checker.run, daemon=True).start()

    def show_update_notification(self, latest_ver, url):
        self._update_url = url
        msg = QMessageBox(self)
        msg.setWindowTitle("Update Available")
        msg.setText(f"Transcript v{latest_ver}")
        msg.setInformativeText("Download now?")
        msg.setStandardButtons(QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if msg.exec() == QMessageBox.StandardButton.Yes:
            webbrowser.open(url)

    def _on_hotkey_press(self):
        mode = self.mode
        if mode == "toggle":
            self._on_toggle()
        elif mode == "push":
            self._on_push_start()
        elif mode == "vad":
            self._on_vad_start()

    def _on_toggle(self):
        if self._transcribing:
            return
        if self._recording:
            self._stop_recording()
        else:
            self._start_recording()

    def _on_push_start(self):
        if self._transcribing or self._recording:
            return
        hotkey = self._config.get("hotkey", "ctrl+alt+r")
        self._push_vk_codes = _parse_hotkey(hotkey)
        self._start_recording()
        self._push_timer.start(32)

    def _on_push_stop(self):
        self._push_timer.stop()
        if self._recording:
            self._stop_recording()

    def _poll_push(self):
        if not self._push_vk_codes:
            self._push_timer.stop()
            return
        any_down = False
        for vk in self._push_vk_codes:
            if ctypes.windll.user32.GetAsyncKeyState(vk) & 0x8000:
                any_down = True
                break
        if not any_down:
            self._on_push_stop()

    def _on_vad_start(self):
        if self._transcribing or self._recording:
            return
        self._start_recording()

    def _on_vad_silence(self):
        if self._recording:
            self._stop_recording()

    def _start_recording(self):
        self._recording = True
        self.mode_indicator.set_blocked(True)
        self.indicator.set_state("recording")
        self.waveform.set_recording(True)
        self.waveform.set_transcribing(False)
        self.recorder.start()
        if self.mode == "vad":
            self.vad.start()
        try:
            sounds.record_start()
        except Exception:
            pass

    def _stop_recording(self):
        self._recording = False
        self.mode_indicator.set_blocked(False)
        self.waveform.set_recording(False)
        self.vad.stop()

        audio = self.recorder.stop()
        if audio is not None and len(audio) > 0:
            self._transcribing = True
            self.waveform.set_transcribing(True)
            if not self.transcriber.model_loaded:
                self.indicator.set_state("loading")
            else:
                self.indicator.set_state("transcribing")
            self.transcriber.transcribe(audio)
        else:
            self.indicator.set_state("idle")
        try:
            sounds.record_stop()
        except Exception:
            pass

    def _on_model_loading(self):
        self.indicator.set_state("loading")

    def _on_transcribe_started(self):
        self.indicator.set_state("transcribing")

    def _on_transcribed(self, text):
        self._transcribing = False
        self.mode_indicator.set_blocked(False)
        self.indicator.set_state("idle")
        self.waveform.set_transcribing(False)
        if text:
            clipboard = QApplication.clipboard()
            clipboard.setText(text)
            if self._config.get("auto_paste", True):
                auto_paste()
            self._flash_border()
            show_notification(
                "Transcript", "Transcription copied"
            )
        else:
            show_notification("Transcript", "No speech detected")
        try:
            sounds.transcribed()
        except Exception:
            pass

    def _flash_border(self):
        self._flash = 0.8
        self._flash_timer.start(16)

    def _on_error(self, error_msg):
        self._transcribing = False
        self.mode_indicator.set_blocked(False)
        self.indicator.set_state("idle")
        self.waveform.set_transcribing(False)
        show_notification(
            "Transcript", f"Transcription failed"
        )
        try:
            sounds.error()
        except Exception:
            pass
