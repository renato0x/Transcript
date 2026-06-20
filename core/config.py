import json
import os

APPDATA = os.environ.get("APPDATA", "")
CONFIG_DIR = os.path.join(APPDATA, "Transcript")
CONFIG_PATH = os.path.join(CONFIG_DIR, "config.json")

DEFAULT_CONFIG = {
    "hotkey": "ctrl+alt+r",
    "language": "pt",
    "auto_paste": True,
    "mode": "toggle",
    "model_size": "small",
    "vad_silence_ms": 1000,
}


def load():
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH) as f:
                return {**DEFAULT_CONFIG, **json.load(f)}
        except Exception:
            pass

    old_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config.json")
    old_path = os.path.normpath(old_path)
    if os.path.exists(old_path):
        try:
            with open(old_path) as f:
                cfg = json.load(f)
            os.makedirs(CONFIG_DIR, exist_ok=True)
            with open(CONFIG_PATH, "w") as f:
                json.dump({**DEFAULT_CONFIG, **cfg}, f, indent=2)
            return {**DEFAULT_CONFIG, **cfg}
        except Exception:
            pass

    os.makedirs(CONFIG_DIR, exist_ok=True)
    save(DEFAULT_CONFIG)
    return dict(DEFAULT_CONFIG)


def save(cfg):
    try:
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(CONFIG_PATH, "w") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass
