"""Test utils to check logs and what they captured"""
# -*- coding: utf-8 -*-

import logging
from contextlib import contextmanager


class LogStreamHandler(logging.Handler):

    def __init__(self, messages, *a, **kw):
        super(LogStreamHandler, self).__init__(*a, **kw)
        self.messages = messages

    def emit(self, record):
        self.messages.append(self.format(record))


@contextmanager
def capture_logs(logger, level=logging.INFO):
    """Use this function to capture logs in your test functions.

    Usage:
    >>> def test_something():
    ...   with capture_logs(logger, logging.INFO) as stream:
    ...     logger.info("My message")
    ...     assert "INFO - My message" in stream
    ...     assert "INFO - My message" == stream[-1]
    """

    stream = []
    handler = LogStreamHandler(stream)
    handler.setLevel(level)
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    handler.setFormatter(formatter)

    logger.addHandler(handler)
    original_level = logger.level
    logger.setLevel(level)
    disabled = logger.disabled
    logger.disabled = False

    yield stream

    logger.removeHandler(handler)
    logger.setLevel(original_level)
    logger.disabled = disabled
