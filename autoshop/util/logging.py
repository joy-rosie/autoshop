import logging
import sys

FORMATTER = logging.Formatter(
    fmt="%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

FILENAME = "autoshop.log"
FILE_HANDLER = logging.FileHandler(FILENAME, mode="w")
FILE_HANDLER.setLevel(logging.DEBUG)
FILE_HANDLER.setFormatter(FORMATTER)

CONSOLE_HANDLER = logging.StreamHandler(stream=sys.stdout)
CONSOLE_HANDLER.setLevel(logging.INFO)
CONSOLE_HANDLER.setFormatter(FORMATTER)


def logger(name: str) -> logging.Logger:
    logger_ = logging.Logger(name=name)
    logger_.addHandler(FILE_HANDLER)
    logger_.addHandler(CONSOLE_HANDLER)
    return logger_
