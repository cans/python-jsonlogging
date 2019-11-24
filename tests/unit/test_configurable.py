# -*- coding: utf-8; -*-
import logging

import yaml

import jsonlogging


def tests_configurable():
    """
    """
    with open('tests/fixtures/config.yml', 'r') as fd:
        config = yaml.safe_load(fd)
    rootlogger = logging.getLogger()

    # When
    logging.config.dictConfig(config)

    # Then
    assert len(rootlogger.handlers) == 1
    handler = rootlogger.handlers[0]
    assert isinstance(handler, logging.StreamHandler)
    assert isinstance(handler.formatter, jsonlogging.Formatter)
    assert len(handler.formatter._keymap) > 0
    assert 'domain' in handler.formatter._keymap['name']
    assert handler.formatter._relative_paths is False

    logging.error('This is a test')


# vim: et:sw=4:syntax=python:ts=4:
