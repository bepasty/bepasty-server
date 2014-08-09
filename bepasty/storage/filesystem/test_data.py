# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

import tempfile

from . import Data


def test():
    f = tempfile.TemporaryFile()

    d = Data(f)
    assert d.size == 0

    d.write('a' * 1024, 0)
    assert d.size == 1024

    d.write('a' * 1024, 1024 * 3)
    assert d.size == 1024 * 4

    try:
        # Python3
        assert d.read(1024, 0) == bytes('a' * 1024, 'utf-8')
        assert d.read(1024, 1024) == bytes('\0' * 1024, 'utf-8')
    except TypeError:
        # Python2
        assert d.read(1024, 0) == 'a' * 1024
        assert d.read(1024, 1024) == '\0' * 1024

    d.close()
