# -*- coding: utf-8; -*-
import logging
import logging_tree

import pytest
try:
    from pythonjsonlogger import jsonlogger
except ImportError:
    jsonlogger = None

import jsonlogging


@pytest.mark.skipif(jsonlogger is None, reason='pythonjsonlogger package is not installed')
@pytest.mark.parametrize('level',
                         [logging.DEBUG, logging.ERROR, logging.INFO, logging.WARNING])
@pytest.mark.parametrize('kwargs',
                         [{'exc_info': True, 'stack_info': True, },
                          {'exc_info': True, 'stack_info': False, },
                          {'exc_info': False, 'stack_info': False, },
                          {'exc_info': False, 'stack_info': True, },
                          ])
def test_pythonjsonlogger(all_attr_fmt,
                          benchmark,
                          kwargs,
                          level,
                          null_handler,
                          null_logger):
    # Given
    null_handler.setFormatter(jsonlogger.JsonFormatter(fmt=all_attr_fmt))
    logging_tree.printout()

    # Then
    benchmark.pedantic(null_logger.log,
                       args=(level, 'message'),
                       kwargs=kwargs,
                       rounds=100,
                       iterations=100)


@pytest.mark.parametrize('level',
                         [logging.DEBUG, logging.ERROR, logging.INFO, logging.WARNING])
@pytest.mark.parametrize('kwargs',
                         [{'exc_info': True, 'stack_info': True, },
                          {'exc_info': True, 'stack_info': False, },
                          {'exc_info': False, 'stack_info': False, },
                          {'exc_info': False, 'stack_info': True, },
                          ])
def test_jsonlogging_with_partial_compiler(all_attr_fmt,
                                           benchmark,
                                           kwargs,
                                           level,
                                           null_handler,
                                           null_logger):
    # Given
    null_handler.setFormatter(jsonlogging.Formatter(fmt=all_attr_fmt))
    logging_tree.printout()

    # Then
    benchmark.pedantic(null_logger.log,
                       args=(level, 'message'),
                       kwargs=kwargs,
                       rounds=100,
                       iterations=100)


@pytest.mark.parametrize('level',
                         [logging.DEBUG, logging.ERROR, logging.INFO, logging.WARNING])
@pytest.mark.parametrize('kwargs',
                         [{'exc_info': True, 'stack_info': True, },
                          {'exc_info': True, 'stack_info': False, },
                          {'exc_info': False, 'stack_info': False, },
                          {'exc_info': False, 'stack_info': True, },
                          ])
def test_jsonlogging_with_closure_compiler(all_attr_fmt,
                                           benchmark,
                                           kwargs,
                                           level,
                                           null_handler,
                                           null_logger):
    # Given
    null_handler.setFormatter(jsonlogging.Formatter(fmt=all_attr_fmt,
                                                    _compiler=jsonlogging.closure_compiler))
    logging_tree.printout()

    # Then
    benchmark.pedantic(null_logger.log,
                       args=(level, 'message'),
                       kwargs=kwargs,
                       rounds=100,
                       iterations=100)


@pytest.mark.parametrize('level',
                         [logging.DEBUG, logging.ERROR, logging.INFO, logging.WARNING])
@pytest.mark.parametrize('kwargs',
                         [{'exc_info': True, 'stack_info': True, },
                          {'exc_info': True, 'stack_info': False, },
                          {'exc_info': False, 'stack_info': False, },
                          {'exc_info': False, 'stack_info': True, },
                          ])
def test_jsonlogging_with_partial_compiler2(all_attr_fmt,
                                            benchmark,
                                            kwargs,
                                            level,
                                            null_handler,
                                            null_logger):
    """Not to be done here.
    """
    # Given
    null_handler.setFormatter(jsonlogging.Formatter(fmt=all_attr_fmt,
                                                    _compiler=jsonlogging.partial_compiler2))
    logging_tree.printout()

    # Then
    benchmark.pedantic(null_logger.log,
                       args=(level, 'message'),
                       kwargs=kwargs,
                       rounds=100,
                       iterations=100)


# vim: et:sw=4:syntax=python:ts=4:
