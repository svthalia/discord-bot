import logging
import re
import sys
import asyncio

from logging import StreamHandler
from logging.handlers import RotatingFileHandler, QueueHandler, QueueListener
from queue import SimpleQueue as Queue
from string import Formatter

import _string


class LocalQueueHandler(QueueHandler):
    def emit(self, record: logging.LogRecord) -> None:
        # Removed the call to self.prepare(), handle task cancellation
        try:
            self.enqueue(record)
        except asyncio.CancelledError as e:
            raise e
        except Exception:
            self.handleError(record)


def get_logger(name=None):
    return logging.getLogger(name)


class FileFormatter(logging.Formatter):
    ansi_escape = re.compile(r"\x1B\[[0-?]*[ -/]*[@-~]")

    def format(self, record):
        record.msg = self.ansi_escape.sub("", record.msg)
        return super().format(record)


class ColouredFormatter(logging.Formatter):
    GREY, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

    RESET_SEQ = "\033[0m"
    COLOR_SEQ = "\033[%dm"
    BOLD_SEQ = "\033[1m"

    COLORS = {
        "DEBUG": WHITE,
        "INFO": CYAN,
        "WARNING": YELLOW,
        "ERROR": RED,
        "CRITICAL": RED,
    }

    def format(self, record):
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = self.BOLD_SEQ + levelname + self.RESET_SEQ
            record.msg = (
                self.COLOR_SEQ % (90 + self.COLORS[levelname])
                + record.msg
                + self.RESET_SEQ
            )
        return logging.Formatter.format(self, record)


def configure_logging(name, level=logging.INFO):
    file_handler = RotatingFileHandler(name, mode="a+", maxBytes=48000, backupCount=1)
    file_handler.setFormatter(
        FileFormatter(
            "%(asctime)s %(name)s[%(lineno)d] - %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    stream_handler = StreamHandler(stream=sys.stdout)
    stream_handler.setFormatter(
        ColouredFormatter(
            "%(asctime)s %(name)s[%(lineno)d] - %(levelname)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    log_queue = Queue()
    queue_handler = LocalQueueHandler(log_queue)

    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    root_logger.addHandler(queue_handler)

    listener = QueueListener(
        log_queue, file_handler, stream_handler, respect_handler_level=True
    )
    listener.start()


class _Default:
    pass


Default = _Default()


class SafeFormatter(Formatter):
    def get_field(self, field_name, args, kwargs):
        first, rest = _string.formatter_field_name_split(field_name)

        try:
            obj = self.get_value(first, args, kwargs)
        except (IndexError, KeyError):
            return "<Invalid>", first

        # loop through the rest of the field_name, doing
        #  getattr or getitem as needed
        # stops when reaches the depth of 2 or starts with _.
        try:
            for n, (is_attr, i) in enumerate(rest):
                if n >= 2:
                    break
                if is_attr:
                    if str(i).startswith("_"):
                        break
                    obj = getattr(obj, i)
                else:
                    obj = obj[i]
            else:
                return obj, first
        except (IndexError, KeyError):
            pass
        return "<Invalid>", first
