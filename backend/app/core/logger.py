import logging
import sys
import os
from logging.handlers import RotatingFileHandler

def setup_logging():
    # Ensure log directory exists
    log_dir = os.path.expanduser("~/.signalsense/logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "signalsense.log")

    # Set up rotating file handler (max 10MB per file, keep 5 backups)
    file_handler = RotatingFileHandler(log_file, maxBytes=10*1024*1024, backupCount=5)
    file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))

    # Console handler for debugging (can be removed in production)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))

    logging.basicConfig(
        level=logging.INFO,
        handlers=[file_handler, console_handler]
    )
    return logging.getLogger("signalsense")

logger = setup_logging()
