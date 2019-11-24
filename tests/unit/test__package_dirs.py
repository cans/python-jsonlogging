# -*- coding: utf-8; -*-
import pytest

import jsonlogging


@pytest.mark.parametrize('filename,expected',
                         [('/usr/lib/pythonX.Y/dist-packages/somelib/somemodule.py',
                           'somelib/somemodule.py'),
                          ('/usr/lib/pythonX.Y/dist-packages/somemodule.py', 'somemodule.py'),
                          ('/usr/lib/pythonX.Y/site-packages/somelib/somemodule.py',
                           'somelib/somemodule.py'),
                          ('/usr/lib/pythonX.Y/site-packages/somemodule.py', 'somemodule.py'),
                          ])
def test__package_dirs_with(filename, expected):
    """Ensures we properly remove prefixes to shorten file path in stack traces.
    """
    re = jsonlogging.Formatter._Formatter__package_dirs

    # When
    match = re.match(filename)

    # Then
    assert match.group(1) == expected


# vim: et:sw=4:syntax=python:ts=4:
