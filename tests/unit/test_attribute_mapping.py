# -*- coding: utf-8; -*-
import json
import logging
import random
import string

import pytest

import jsonlogging


@pytest.mark.parametrize('attribute', jsonlogging.LOG_RECORD_ATTRS)
@pytest.mark.parametrize('level', [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR])
def test_attribute_can_be_mapped(attribute, handler, level, logger):
    # Given
    alt_key = ''.join(random.choice(string.ascii_letters) for i in range(25))
    handler.setFormatter(jsonlogging.Formatter(fmt='{{{}}}'.format(attribute),
                                               style='{',
                                               keymap={attribute: alt_key}))

    # When
    logger.log(level, 'message', stack_info=True, exc_info=True)

    # Then
    entry = list(handler.level_logs(level))[0]
    entry = json.loads(entry)
    assert attribute not in entry
    assert alt_key in entry
    assert entry[alt_key] is not None


@pytest.mark.parametrize('attribute', jsonlogging.LOG_RECORD_ATTRS)
@pytest.mark.parametrize('level', [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR])
def test_attribute_can_be_mapped_v2(attribute, handler, level, logger):
    # Given
    alt_key = ''.join(random.choice(string.ascii_letters) for i in range(25))
    handler.setFormatter(jsonlogging.Formatter(fmt='{{{}}}'.format(attribute),
                                               style='{',
                                               keymap={attribute: alt_key},
                                               _compiler=jsonlogging.partial_compiler3))

    # When
    logger.log(level, 'message', stack_info=True, exc_info=True)

    # Then
    entry = list(handler.level_logs(level))[0]
    entry = json.loads(entry)
    assert attribute not in entry
    assert alt_key in entry
    assert entry[alt_key] is not None


# vim: et:sw=4:syntax=python:ts=4:
