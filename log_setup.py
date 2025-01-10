import logging
from datetime import date
import os

LOG_DIR = "logs"


def create_log_dir() -> None:

    if not os.path.isdir(LOG_DIR):
        os.mkdir(LOG_DIR)
    if not os.path.isdir(LOG_DIR + "/failure_logs/"):
        os.mkdir(LOG_DIR + "/failure_logs/")
    if not os.path.isdir(LOG_DIR + "/info_logs/"):
        os.mkdir(LOG_DIR + "/info_logs/")


def log_setup() -> logging.Logger:
    """
    Set up logging configuration.
    """
    create_log_dir()

    logger = logging.getLogger(__name__)

    class InfoFilterer(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            return record.levelno == logging.INFO

    class DebugFormatFilterer(logging.Filter):
        def filter(self, record: logging.LogRecord) -> bool:
            return record.levelno != logging.INFO

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    handler_debug = logging.FileHandler(f"{LOG_DIR}/failure_logs/{date.today()}.log")
    handler_debug.setFormatter(formatter)
    handler_debug.setLevel(logging.DEBUG)
    handler_debug.addFilter(DebugFormatFilterer())

    handler_info = logging.FileHandler(f"{LOG_DIR}/info_logs/{date.today()}.log")
    handler_info.setFormatter(formatter)
    handler_info.setLevel(logging.INFO)
    handler_info.addFilter(InfoFilterer())

    logger.addHandler(handler_debug)
    logger.addHandler(handler_info)
    logger.setLevel(logging.DEBUG)

    return logger
