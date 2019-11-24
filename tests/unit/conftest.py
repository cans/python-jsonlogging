# -*- coding: utf-8; -*-
from collections import defaultdict
import copy
import logging

import pytest


class DebugHandler(logging.Handler):
    """An in-memory handler that lets you inspect the logs it emitted."""

    level_map = {'debug': logging.DEBUG,
                 'info': logging.INFO,
                 'warning': logging.WARNING,
                 'error': logging.ERROR,
                 }

    def __init__(self):
        """An in-memory handler that lets you inspect the logs it emitted.

        You can access all logs with its :attr:`DebugHandler.logs`, or
        logs from a specific level using :attr:`DebugHandler.debug_logs`,
        :attr:`DebugHandler.info_logs`, *etc.*

        Warning:

        This handler is not intended for
        """
        self._logs = []
        self._categorized_logs = defaultdict(list)
        super().__init__(level=logging.DEBUG)

    def __getattr__(self, attrname):
        if attrname.endswith('logs'):
            try:
                level, logs = attrname.split('_')
                level = self.level_map[level]
            except ValueError:
                level = None
            except KeyError:
                if level == 'level':
                    return self._logs_iterator
                raise TypeError("{} object has no attribute '{}'"
                                .format(self.__class__.__name__, attrname))
            return self._logs_iterator(level)

        # Falling through the default implementation
        return self.__dict__[attrname]

    def _logs_iterator(self, level=None):
        if level is None:
            logs = self._logs
        else:
            logs = self._categorized_logs[level]

        for log in logs:
            yield log

    def emit(self, record: logging.LogRecord):
        """Emits the formatted log record in to logs
        """
        log = self.formatter.format(record)
        self._logs.append(log)
        self._categorized_logs[record.levelno].append(log)


@pytest.fixture
def handler():
    """Provides a DebugHandler instance.
    """
    yield DebugHandler()


@pytest.fixture
def logger(handler):
    """Create a logger isolated from others.

    Isolation comes from setting propagate to ``False``: test logs
    will not pollute "normal" logs. If it were ``True`` the log record
    would be passed along to the root logger that would apply its own
    handler to it.

    """
    the_logger = logging.getLogger('out_of_tree_logger')
    the_logger.propagate = False
    the_logger.addHandler(handler)
    the_logger.setLevel(logging.DEBUG)
    # 'cause when we play with `disable_existing_loggers`, this can become disabled.
    the_logger.disabled = False

    yield the_logger

    handler.flush()  # Does removeHandler() does that ?
    the_logger.removeHandler(handler)  # So we do not add an additional


@pytest.fixture
def args():
    # Copy to make sure each test receives a fresh, unmutated dict.
    return copy.copy({'asctime': '2019-01-01T00:00:00.000Z',
                      'level': 'DEBUG',
                      'module': '__main__',
                      'message': 'A less than 50 chars ling string.',
                      })


# vim: et:sw=4:syntax=python:ts=4:
