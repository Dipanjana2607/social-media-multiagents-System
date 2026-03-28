import logging
import sys


def setup_logging(level: str = "INFO"):
    fmt = "%(asctime)s %(levelname)s %(name)s: %(message)s"
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO), format=fmt, stream=sys.stdout)

    # Ensure uvicorn loggers use the same handlers/format
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access"):
        logger = logging.getLogger(name)
        logger.handlers = logging.getLogger().handlers
        logger.setLevel(getattr(logging, level.upper(), logging.INFO))


def get_logger(name: str | None = None):
    return logging.getLogger(name or __name__)
