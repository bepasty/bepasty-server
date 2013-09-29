# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

import tempfile

from . import Item


def test():
    f1 = tempfile.TemporaryFile()
    f2 = tempfile.TemporaryFile()

    with Item(f1, f2) as i:
        assert i.data is not None
        assert i.meta is not None
