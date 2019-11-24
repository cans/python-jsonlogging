# -*- coding: utf-8; -*-
import pytest
import jsonlogging


@pytest.fixture
def all_attr_fmt():
    """Returns a Formatter format string that includes all LogRecord attributes.
    """
    return '{{{}}}'.format('} {'.join(jsonlogging.LOG_RECORD_ATTRS))


# vim: et:sw=4:syntax=python:ts=4:
