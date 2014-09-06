# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

from . import Item


def test(tmpdir):
    pm = tmpdir.join("test.meta")
    pd = tmpdir.join("test.data")

    with Item(pm.open('w+b'), pd.open('w+b')) as i:
        assert i.data is not None
        assert i.meta is not None
