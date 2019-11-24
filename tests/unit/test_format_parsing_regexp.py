# -*- coding: utf-8; -*-
from jsonlogging import _brace_parser, _dollar_parser, _percent_parser


def test_brace_logging_re(args):
    # Given
    fmt = '{asctime} {level:3s} content we do {module:} not care about {message:50s}'

    # When
    matches = _brace_parser(fmt)

    # Then
    assert len(matches) == 4
    assert [key for key, _ in matches] == ['asctime', 'level', 'module', 'message']
    assert [frmt for _, frmt in matches] == ['', '3s', '', '50s']


def test__dollar_parser(args):
    # Given
    fmt = (r'$asctime ${level} content we do $module $$ not ${} $ $$$pathname \$nope care about'
           ' ${message}')

    # When
    matches = _dollar_parser(fmt)

    # Then
    assert len(matches) == 5
    assert [key for key, _ in matches] == ['asctime', 'level', 'module', 'pathname', 'message']


def test__percent_parser():
    # Given
    fmt = '%(asctime)s content we 100% do not care about %(message)s %()s \\%(levelno)d %%(module)s'

    # When
    keys = _percent_parser(fmt)

    # Then
    assert len(keys) == 3
    assert keys == [('asctime', 's'), ('message', 's'), ('levelno', 'd')]


# vim: et:sw=4:syntax=python:ts=4:
