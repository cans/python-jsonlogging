# -*- coding: utf-8; -*-
"""Takes a logger and ensures its methods output is as expected
"""
import json
import logging
import sys

import pytest

import jsonlogging


@pytest.mark.parametrize('compiler',
                         [jsonlogging.partial_compiler,
                          jsonlogging.partial_compiler2,
                          jsonlogging.partial_compiler3,
                          jsonlogging.closure_compiler,
                          jsonlogging.closure_compiler2,
                          ])
def test_logger_with_all_attributes(logger, handler, all_attr_fmt, compiler):
    # Given
    fmt = 'greeting: %s'
    args = ('hello', )
    formatter = jsonlogging.Formatter(fmt=all_attr_fmt, style='{', _compiler=compiler)
    handler.setFormatter(formatter)

    # When
    logger.debug(fmt, *args)
    logger.info(fmt, *args)
    logger.warning(fmt, *args)
    logger.error(fmt, args)
    try:
        raise ValueError('Exception type does not really matter, but do not'
                         ' use `Exception` or your linter will complain.')
    except ValueError:
        logger.exception(fmt, *args)

    # Then
    for log in handler.logs:
        log = json.loads(log)
        assert list(log.keys()) == list(jsonlogging.LOG_RECORD_ATTRS)


def test_logger_with_extra(logger, handler, all_attr_fmt):
    # Given
    fmt = 'greeting: %s'
    args = ('hello', )
    formatter = jsonlogging.Formatter(fmt=all_attr_fmt, style='{')
    handler.setFormatter(formatter)

    # When
    logger.debug(fmt, *args, extra={'k': 'v'})
    logger.info(fmt, *args, extra={'k': 'v'})
    logger.warning(fmt, *args, extra={'k': 'v'})
    logger.error(fmt, args, extra={'k': 'v'})
    try:
        raise ValueError('Exception type does not really matter, but do not'
                         ' use `Exception` or your linter will complain.')
    except ValueError:
        logger.exception(fmt, *args, extra={'k': 'v'})

    # Then
    expected_keys = jsonlogging.LOG_RECORD_ATTRS + ('k', )
    for log in handler.logs:
        log = json.loads(log)
        assert list(log.keys()) == list(expected_keys)


@pytest.mark.parametrize('level',
                         [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR])
def test_logger_log_with_stack_info_equal_true_format_stacks_true(level,
                                                                  logger,
                                                                  handler,
                                                                  all_attr_fmt):
    # Given
    fmt = 'greeting: %s'
    args = ('hello', )
    formatter = jsonlogging.Formatter(fmt=all_attr_fmt, style='{', format_stacks=True)
    handler.setFormatter(formatter)

    # When
    logger.log(level, fmt, *args, stack_info=True)
    log_entry = json.loads(list(handler.level_logs(level))[0])

    # Then
    assert 'stack_info' in log_entry
    assert 'frames' in log_entry['stack_info']


@pytest.mark.parametrize('level',
                         [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR])
def test_logger_log_with_stack_info_equal_true_format_stacks_false(level,
                                                                   logger,
                                                                   handler,
                                                                   all_attr_fmt):
    # Given
    fmt = 'greeting: %s'
    args = ('hello', )
    formatter = jsonlogging.Formatter(fmt=all_attr_fmt, style='{')
    handler.setFormatter(formatter)

    # When
    logger.log(level, fmt, *args, stack_info=True)
    log_entry = json.loads(list(handler.level_logs(level))[0])

    # Then
    assert 'stack_info' in log_entry
    assert isinstance(log_entry['stack_info'], str)


@pytest.mark.parametrize('level',
                         [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR])
def test_logger_log_with_exc_info_equal_true(level, logger, handler, all_attr_fmt):
    # Given
    fmt = 'greeting: %s'
    args = ('hello', )
    formatter = jsonlogging.Formatter(fmt=all_attr_fmt, style='{')
    handler.setFormatter(formatter)

    # When
    logger.log(level, fmt, *args, exc_info=True)
    log_entry = json.loads(list(handler.level_logs(level))[0])

    # Then
    assert 'exc_info' in log_entry
    assert 'frames' in log_entry['exc_info']
    assert isinstance(log_entry['exc_info']['frames'], list)
    assert 'value' in log_entry['exc_info']
    assert log_entry['exc_info']['value'] is None


def log_and_quit_when_depth_reached(depth, logger, level, msg, *args, _depth=None, **kwargs):
    if _depth == 1:
        logger.log(level, msg, *args, **kwargs)
    else:
        assert depth > 1
        log_and_quit_when_depth_reached(depth,
                                        logger,
                                        level,
                                        msg,
                                        *args,
                                        _depth=depth - 1 if _depth is None else _depth - 1,
                                        **kwargs)


@pytest.mark.skipif(sys.version_info < (3, 8), reason="requires python3.8 or higher")
@pytest.mark.parametrize('level',
                         [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR])
def test_logger_log_with_stacklevel_below_stack_depth(level, logger, handler, all_attr_fmt):
    # Given
    fmt = 'greeting: %s'
    args = ('hello', )
    formatter = jsonlogging.Formatter(fmt=all_attr_fmt, style='{')
    handler.setFormatter(formatter)

    # When
    log_and_quit_when_depth_reached(10, logger, level, fmt, *args, stack_info=True, stack_level=5)

    # Then
    logs = list(handler.level_logs(level))
    assert len(logs) == 1
    log_entry = json.loads(logs[0])
    assert 'exc_info' in log_entry
    assert 'frames' in log_entry['stack_info']
    assert isinstance(log_entry['stack_info']['frames'], list)
    assert len(log_entry['stack_info']['frames']) == 5


# vim: et:sw=4:syntax=python:ts=4:
