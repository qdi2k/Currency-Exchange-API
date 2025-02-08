import logging
import logging.config
import os

from uvicorn import logging as uvicorn_logging

from app.core.config import BASE_DIR, settings

LOG_LEVEL: str = "DEBUG" if settings.DEBUG else "INFO"
FORMAT_UVICORN: str = (
    "%(levelprefix)s %(asctime)s" + " - %(filename)s - %(message)s"
)
FORMAT_SIMPLE: str = (
    "%(asctime)s - %(levelname)s" + " - %(filename)s - %(message)s"
)
FORMAT_DATE: str = "%Y-%m-%d %H:%M:%S"
LOG_FILE: str = "info.log"
LOG_FILE: str = os.path.join(BASE_DIR, "logs", LOG_FILE)


def init_loggers() -> logging.Logger:
    """Инициализация параметров логирования."""
    logs_dir = os.path.join(BASE_DIR, "logs")
    if not os.path.exists(logs_dir):
        os.makedirs(logs_dir)

    logger: logging.Logger = logging.getLogger()
    logger.setLevel(level=LOG_LEVEL)

    console_formatter: uvicorn_logging.DefaultFormatter = (
        uvicorn_logging.DefaultFormatter(
            fmt=FORMAT_UVICORN, datefmt=FORMAT_DATE
        )
    )
    console_handler: logging.StreamHandler = logging.StreamHandler()
    console_handler.setFormatter(fmt=console_formatter)
    console_handler.setLevel(level=LOG_LEVEL)

    file_formatter: logging.Formatter = logging.Formatter(
        fmt=FORMAT_SIMPLE, datefmt=FORMAT_DATE
    )
    file_handler: logging.FileHandler = logging.FileHandler(filename=LOG_FILE)
    file_handler.setFormatter(fmt=file_formatter)
    file_handler.setLevel(level=LOG_LEVEL)

    logger.addHandler(hdlr=console_handler)
    logger.addHandler(hdlr=file_handler)

    return logger
