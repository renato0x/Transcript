import os
import logging
from logging.handlers import RotatingFileHandler

LOG_DIR = os.path.join(os.environ.get("APPDATA", ""), "Transcript", "logs")


def setup_logger():
    os.makedirs(LOG_DIR, exist_ok=True)
    log_path = os.path.join(LOG_DIR, "app.log")

    handler = RotatingFileHandler(log_path, maxBytes=1_048_576, backupCount=3, encoding="utf-8")
    handler.setFormatter(logging.Formatter("[%(asctime)s] %(levelname)s: %(message)s"))

    logger = logging.getLogger("Transcript")
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)

    return logger
