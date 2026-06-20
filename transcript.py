import sys
import os
import ctypes
import traceback
import threading

from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import QObject, Signal, QAbstractNativeEventFilter, QTimer
from PySide6.QtGui import QIcon

from widgets.floating_window import FloatingWindow
from core import config as cfg
from core.logger import setup_logger
from core.updater import UpdateChecker
from version import VERSION

WM_HOTKEY = 0x0312
MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
MOD_WIN = 0x0008

_MOD_MAP = {
    "ctrl": MOD_CONTROL,
    "alt": MOD_ALT,
    "shift": MOD_SHIFT,
    "win": MOD_WIN,
}

_HOTKEY_ID = 1

logger = None


def _resource_path(rel_path):
    try:
        base = sys._MEIPASS
    except AttributeError:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, rel_path)


def _parse_hotkey_vk(hotkey_str):
    mod = 0
    vk = 0
    for p in hotkey_str.lower().split("+"):
        if p in _MOD_MAP:
            mod |= _MOD_MAP[p]
        elif len(p) == 1:
            vk = ord(p.upper())
    return mod, vk if vk else ord("R")


class _Win32HotkeyFilter(QAbstractNativeEventFilter):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback

    def nativeEventFilter(self, eventType, message):
        if eventType == b"windows_generic_MSG":
            msg = ctypes.wintypes.MSG.from_address(int(message))
            if msg.message == WM_HOTKEY:
                self.callback()
                return True, 0
        return False, 0


class HotkeyManager(QObject):
    press = Signal()

    def __init__(self, window):
        super().__init__(window)
        cfg_ = cfg.load()
        hotkey = cfg_.get("hotkey", "ctrl+alt+r")
        mod, vk = _parse_hotkey_vk(hotkey)

        self._filter = _Win32HotkeyFilter(self.press.emit)
        QApplication.instance().installNativeEventFilter(self._filter)

        hwnd = int(window.winId())
        ret = ctypes.windll.user32.RegisterHotKey(hwnd, _HOTKEY_ID, mod, vk)
        if not ret:
            logger and logger.warning("Falha ao registrar hotkey %s", hotkey)

    def cleanup(self):
        try:
            parent = self.parent()
            hwnd = int(parent.winId())
            ctypes.windll.user32.UnregisterHotKey(hwnd, _HOTKEY_ID)
        except Exception:
            pass


def _handle_exception(exc_type, exc_value, exc_tb):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_tb)
        return
    if logger:
        logger.critical("Erro nao tratado", exc_info=(exc_type, exc_value, exc_tb))
    tb_text = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    msg = QMessageBox()
    msg.setIcon(QMessageBox.Icon.Critical)
    msg.setWindowTitle("Transcript")
    msg.setText("Unexpected error.")
    msg.setInformativeText(
        "Details saved to:\n"
        f"{os.path.join(os.environ.get('APPDATA', ''), 'Transcript', 'logs', 'app.log')}"
    )
    msg.setDetailedText(tb_text)
    msg.exec()


def main():
    global logger
    logger = setup_logger()
    logger.info("Transcript %s started", VERSION)

    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, "Local\\Transcript")
    if ctypes.windll.kernel32.GetLastError() == 183:
        ctypes.windll.kernel32.CloseHandle(mutex)
        return

    sys.excepthook = _handle_exception

    app = QApplication(sys.argv)
    app.setApplicationName("Transcript")
    app.setApplicationVersion(VERSION)
    app.setOrganizationName("renato0x")

    ico_path = _resource_path("logo.ico")
    if os.path.exists(ico_path):
        app.setWindowIcon(QIcon(ico_path))

    qss_path = _resource_path("style.qss")
    if os.path.exists(qss_path):
        with open(qss_path) as f:
            app.setStyleSheet(f.read())

    window = FloatingWindow()
    window.show()

    hotkey = HotkeyManager(window)
    hotkey.press.connect(window._on_hotkey_press)
    app.aboutToQuit.connect(hotkey.cleanup)

    checker = UpdateChecker()
    checker.found.connect(lambda v, u: QTimer.singleShot(0, lambda: window.show_update_notification(v, u)))
    threading.Thread(target=checker.run, daemon=True).start()

    exit_code = app.exec()

    ctypes.windll.kernel32.CloseHandle(mutex)
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
