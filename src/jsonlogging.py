# -*- coding: utf-8; -*-
# import datetime
import functools
import json
import logging
import logging.config
import operator
import os
import re
import traceback
from typing import Any, Callable, Iterable, List, Mapping, Optional, Tuple, Type, Union
import warnings


LOG_RECORD_ATTRS = ('asctime',
                    'created',
                    'exc_info',
                    # 'exc_text',
                    'filename',
                    'funcName',
                    'levelname',
                    'levelno',
                    'lineno',
                    'module',
                    'msecs',
                    'message',
                    'name',
                    'pathname',
                    'process',
                    'processName',
                    'relativeCreated',
                    'stack_info',
                    'thread',
                    'threadName',
                    )
#: The attributes of a :class:`logging.LogRecord` that can be displayed in a log entry.

_ALL_LOG_RECORD_ATTRS = ('args',
                         'asctime',
                         'created',
                         'exc_info',
                         'exc_text',
                         'filename',
                         'funcName',
                         'getMessage',
                         'levelname',
                         'levelno',
                         'lineno',
                         'message',
                         'module',
                         'msecs',
                         'msg',
                         'name',
                         'pathname',
                         'process',
                         'processName',
                         'relativeCreated',
                         'stack_info',
                         'thread',
                         'threadName',
                         )
#: All default attributes of a :class:`logging.LogRecord` as opposed to extra ones a
#: user can provide with the ``extra`` argument, e.g.::
#:
#:    logging.log(<level>, <pattern>, *<pattern-args>, extra=<extra attributes>)
#:

BRACE_FORMAT_PARSER = re.compile(r'(?:\{)(?P<key>[^:\}]+)(?:(?::(?P<fmt>[^}]*))?\})')
DOLLAR_FORMAT_PARSER = re.compile(r'(?:(?<!\\)\$(?:(:?\$\$)*\{(?=[^ ]+\}))?)(?P<key>[^\$\{ \}]+)'
                                  r'(?:\})?')
PERCENT_FORMAT_PARSER = re.compile(r'(?:(?<!%)%(?:(?=(?:%%)*\())%*\()(?P<key>[^)]+)'
                                   r'(?:\)(?P<fmt>[^ds]*[ds]))')


def _brace_parser(fmt) -> Iterable[Tuple[str, str]]:
    """Parses '{'-style log format string to extract the keys to put in the JSON object.
    """
    return BRACE_FORMAT_PARSER.findall(fmt)


def _dollar_parser(fmt) -> Iterable[Tuple[str, str]]:
    """Parses '$'-style log format string to extract the keys to put in the JSON object.
    """
    return list((x, '') for _, x in DOLLAR_FORMAT_PARSER.findall(fmt))


def _percent_parser(fmt):
    """Parses '%'-style log format string to extract the keys to put in the JSON object.
    """
    return PERCENT_FORMAT_PARSER.findall(fmt)


FORMAT_PARSERS = (('{', _brace_parser),
                  ('$', _dollar_parser),
                  ('%', _percent_parser),
                  )


def _dater(formatter, fmt, record) -> str:
    """Formats the timestamp of a LogRecord in a human readable way.
    """
    return fmt.format(formatter.formatTime(record))


def _dater2(formatter, record) -> str:
    """Formats the timestamp of a LogRecord in a human readable way.
    """
    return formatter.formatTime(record)


def _exceptioner(formatter, record) -> Optional[List[Tuple[str, str]]]:
    """Formats the exc_info attribute of a LogRecord, if set.
    """
    if record.exc_info:
        return formatter.formatException(record.exc_info)
    return None


def _formatter(attr, fmt, record) -> str:
    """Formats scalar LogRecord attributes.
    """
    return fmt.format(getattr(record, attr))


def _formatter2(attr, record) -> str:
    """Formats scalar LogRecord attributes.
    """
    return getattr(record, attr)


def _messager(fmt, record):
    """Formats the message of a LogRecord.
    """
    return fmt.format(record.getMessage())


def _messager2(record):
    """Formats the message of a LogRecord.
    """
    return record.getMessage()


def _stacker(formatter, record) -> Optional[List[Tuple[str, str]]]:
    if record.stack_info:
        return formatter.formatStack(record.stack_info)
    return None


def closure_compiler(formatter, attr, fmt):
    """Compiles the formatting pattern into a callable that take a single argument: a log record.

    This compiler is implemented using closures
    """
    if attr == 'message':
        def _closure_messager(record):
            return fmt.format(record.getMessage())
        return _closure_messager

    if attr == 'asctime':
        def _closure_dater(record) -> str:
            return fmt.format(formatter.formatTime(record))

        return _closure_dater

    if attr == 'exc_info':
        def _closure_exceptioner(record) -> Optional[List[Tuple[str, str]]]:
            if record.exc_info:
                return formatter.formatException(record.exc_info)
            return None
        return _closure_exceptioner

    if attr == 'stack_info':
        def _closure_stacker(record) -> Optional[List[Tuple[str, str]]]:
            if record.stack_info:
                return formatter.formatStack(record.stack_info)
            return None
        return _closure_stacker

    def _closure_formatter(record) -> str:
        return fmt.format(getattr(record, attr))

    return _closure_formatter


def closure_compiler2(formatter, attr):
    """Compiles the formatting pattern into a callable that take a single argument: a log record.

    This compiler is implemented using closures
    """
    if attr == 'message':
        def _closure_messager(record):
            return record.getMessage()
        return _closure_messager

    if attr == 'asctime':
        def _closure_dater(record) -> str:
            return formatter.formatTime(record)

        return _closure_dater

    if attr == 'exc_info':
        def _closure_exceptioner(record) -> Optional[List[Tuple[str, str]]]:
            if record.exc_info:
                return formatter.formatException(record.exc_info)
            return None
        return _closure_exceptioner

    if attr == 'stack_info':
        def _closure_stacker(record) -> Optional[List[Tuple[str, str]]]:
            if record.stack_info:
                return formatter.formatStack(record.stack_info)
            return None
        return _closure_stacker

    def _closure_formatter(record) -> str:
        return getattr(record, attr)

    return _closure_formatter


def partial_compiler(formatter, attr, fmt) -> Callable[[logging.LogRecord], Union[str, int, float]]:
    """Compiles the formatting pattern into a callable that take a single argument: a log record.

    This compiler is implemented using partial functions.
    """
    if attr == 'message':
        return functools.partial(_messager, fmt)

    if attr == 'asctime':
        return functools.partial(_dater, formatter, fmt)

    if attr == 'exc_info':
        return functools.partial(_exceptioner, formatter)

    if attr == 'stack_info':
        return functools.partial(_stacker, formatter)

    return functools.partial(_formatter, attr, fmt)


def partial_compiler2(formatter: logging.Formatter,
                      attr: str
                      ) -> Callable[[logging.LogRecord], Union[str, int, float]]:
    """Compiles the formatting pattern into a callable that take a single argument: a log record.

    This compiler is implemented using partial functions.
    """
    return functools.partial(*{'message': (_messager2, ),
                               'asctime': (_dater2, formatter),
                               'exc_info': (_exceptioner, formatter),
                               'stack_info': (_stacker, formatter),
                               }.get(attr, (_formatter2, attr))
                             )


def partial_compiler3(formatter: logging.Formatter,
                      attr: str
                      ) -> Callable[[logging.LogRecord], Union[str, int, float]]:
    """Compiles the formatting pattern into a callable that take a single argument: a log record.

    This compiler is implemented using partial functions.
    """
    return {'message': functools.partial(_messager2),
            'asctime': functools.partial(_dater2, formatter),
            'exc_info': functools.partial(_exceptioner, formatter),
            'stack_info': functools.partial(_stacker, formatter),
            }.get(attr, operator.attrgetter(attr))


class Formatter(logging.Formatter):
    """A :class:`logging.Formatter<py3>` implementation that encodes log records as JSON objects.
    """

    __slots__ = ('_keymap', '_datefmt', '_raw_fmt', '_compiler')
    __package_dirs = re.compile('(?:.*)(?:' + os.sep + '(?:site|dist)-packages' + os.sep + ')(.*)')
    __code_location = re.compile(r'^(?:  File ")([^"]*)(?:", line )([0-9]+)(?:, in )(.*)$')

    def __init__(self,
                 fmt: str = None,
                 datefmt: str = None,
                 format_stacks: bool = False,
                 keymap: Mapping[str, str] = None,
                 relative_paths: bool = False,
                 style: str = '%',
                 _compiler: Callable[['Formatter', str, str],
                                     Callable[[logging.LogRecord],
                                              Union[str, int, float]]] = partial_compiler,
                 ) -> None:
        """Initializes a JSON encoding LogRecord Formatter.

        The ``fmt``, ``datefmt`` and ``style`` behave as in the
        :ref:`logging.Formatter<py:formatter-objects>`.

        Arguments:
            keymap: a dictionary to map LogRecord attribute names to alternate
                keys in the JSON output. *E.g.* to rename 'asctime' to 'timestamp',
                pass the keymap ``{'asctime': 'timestamp'}``.
            relative_paths: whether to remove the site package prefix from files
                path in stack traces, to saves some bytes (can prove usefull if
                logs are shipped through a network).



        Warnings:

        We use regular expression to parse the format string. It is a well known
        that regular expressions cannot do, like counting.
        """
        super().__init__(fmt, datefmt=datefmt, style=style)  # TODO: python3.8 add: , validate=True

        keymap = keymap or dict()
        # Ensure we only keep valid LogRecord attribute names.
        if _compiler in {partial_compiler3, partial_compiler2, closure_compiler2}:
            selected_attrs = {a: a
                              for a, f in dict(FORMAT_PARSERS)[style](fmt) if a in LOG_RECORD_ATTRS}
            self._keymap = {keymap.get(a, a): _compiler(self, a)
                            for a, _ in selected_attrs.items()}
            self.format = self._format2

        else:
            selected_attrs = {a: (a, f)
                              for a, f in dict(FORMAT_PARSERS)[style](fmt) if a in LOG_RECORD_ATTRS}
            self._keymap = {a: (keymap.get(k, k),
                                _compiler(self,
                                          a,
                                          '{{{}{}}}'.format(':' if selected_attrs[a][1] else '',
                                                            selected_attrs[a][1])),
                                )
                            for a, (k, f) in selected_attrs.items()}
            self.format = self._format1

        # self._datefmt = datefmt or '%Y-%m-%dT%H:%M:%S.%f'
        self._raw_fmt = fmt  # TODO: only useful for debug, remove ?
        self._relative_paths = relative_paths
        self._blob = not format_stacks

        unknown_keys = set(keymap.keys()) - set(selected_attrs.keys())
        if unknown_keys:
            warnings.warn('Your configuration contains unknown log record keys: {}'
                          .format(', '.join(unknown_keys)))
        if not selected_attrs:  # TODO: this is what Py3.8 validate kwarg is for.
            warnings.warn('No attributes to seralize to JSON ! '
                          'The format string and format style you selected may not match')

    def _format1(self, record: logging.LogRecord) -> str:
        output = {k: f(record) for a, (k, f) in self._keymap.items()}
        output.update({k: str(getattr(record, k))
                       for k in dir(record)
                       if k not in _ALL_LOG_RECORD_ATTRS and not k.startswith('__')})
        return json.dumps(output, separators=(',', ':'))

    def _format2(self, record: logging.LogRecord) -> str:
        output = {k: f(record) for k, f in self._keymap.items()}
        output.update({k: str(getattr(record, k))
                       for k in dir(record)
                       if k not in _ALL_LOG_RECORD_ATTRS and not k.startswith('__')})
        return json.dumps(output, separators=(',', ':'))

    # def formatTime(self, record: logging.LogRecord, datefmt: Optional[str] = None):
    #     datefmt = datefmt or self._datefmt
    #     timestamp = datetime.datetime.fromtimestamp(record.created, tz=datetime.timezone.utc)
    #     if datefmt:
    #         return timestamp.strftime(datefmt)
    #     return timestamp.isoformat()

    def formatException(self, exc_info: Tuple[Type[BaseException], Exception, Any]):
        """Formats exceptions as a JSON serializable object.
        """
        tb_frames = []
        type_, value, tbk = exc_info

        if self._relative_paths is True:
            for filename, lineno, code, line in traceback.extract_tb(tbk):
                filename = self._relativize(filename)
                tb_frames.append((filename, lineno, code, line))
        else:
            tb_frames = list(tuple(f) for f in traceback.extract_tb(tbk))

        return {'value': None if value is None else str(value),
                'type': getattr(type_, '__name__', str(type_)),
                'frames': tb_frames,
                }

    def _relativize(self, filename):
        match = self.__package_dirs.match(filename)
        if match:
            return match.group(1)

        return filename

    def formatStack(self, stack_info):
        if self._blob:
            return stack_info
        else:
            stack_frames = []

            stack_info_lines = stack_info.split('\n')[1:]
            for location, line in zip(stack_info_lines[0::2], stack_info_lines[1::2]):
                match = self.__code_location.match(location)
                filename, lineno, code = ('?', '?', '?') if match is None else match.groups()
                if self._relative_paths:
                    filename = self._relativize(filename)
                stack_frames.append((filename, lineno, code, line))

        # else:  # TODO: Appears we never receive something other than a string. DEAD CODE
        #     if self._relative_path is True:
        #         for filename, lineno, code, line in traceback.extract_stack():
        #             if filename[0] == '<':
        #                 stack_frames.append((filename, lineno, code, line))
        #                 continue
        #             match = self.__package_dirs.match(filename)
        #             if match:
        #                 stack_frames.append((match.group(1), lineno, code, line))
        #                 continue
        #             stack_frames.append((filename, lineno, code, line))
        #     else:
        #         stack_frames = list(traceback.extract_stack(stack_info))
        return {'frames': stack_frames}


# vim: et:sw=4:syntax=python:ts=4:
