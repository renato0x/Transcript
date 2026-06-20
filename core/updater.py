import json
import urllib.request
import urllib.error
from PySide6.QtCore import QObject, Signal
from version import VERSION

GITHUB_API = "https://api.github.com/repos/renato0x/transcript/releases/latest"


class UpdateChecker(QObject):
    found = Signal(str, str)

    def run(self):
        try:
            req = urllib.request.Request(GITHUB_API, headers={"User-Agent": "Transcript"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
                latest = data.get("tag_name", "").lstrip("v")
                if latest and _parse_version(latest) > _parse_version(VERSION):
                    self.found.emit(latest, data.get("html_url", ""))
        except Exception:
            pass


def _parse_version(v):
    parts = v.split(".")
    return tuple(int(p) if p.isdigit() else 0 for p in parts)
