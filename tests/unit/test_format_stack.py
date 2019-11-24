# -*- coding: utf-8; -*-
import json
import jsonlogging


def test_format_stack_with_relative_paths(all_attr_fmt, handler, logger):
    # Given
    formatter = jsonlogging.Formatter(all_attr_fmt,
                                      style='{',
                                      relative_paths=True,
                                      format_stacks=True)
    handler.setFormatter(formatter)

    # When
    logger.debug('debug message', stack_info=True)

    # Then
    log_entry = json.loads(list(handler.debug_logs)[0])
    assert 'stack_info' in log_entry
    assert 'frames' in log_entry['stack_info']
    for filename, _, _, _ in log_entry['stack_info']['frames']:
        assert ('/' == filename[0] and '-packages/' not in filename) or '/' != filename[0]


def test_format_stack_without_relative_paths(all_attr_fmt, handler, logger):
    # Given
    formatter = jsonlogging.Formatter(all_attr_fmt,
                                      style='{',
                                      relative_paths=False,
                                      format_stacks=True)
    handler.setFormatter(formatter)

    # When
    logger.debug('debug message', stack_info=True)

    # Then
    log_entry = json.loads(list(handler.debug_logs)[0])
    assert 'stack_info' in log_entry
    assert 'frames' in log_entry['stack_info']
    for filename, _, _, _ in log_entry['stack_info']['frames']:
        assert '/' == filename[0]


# vim: et:sw=4:syntax=python:ts=4:
