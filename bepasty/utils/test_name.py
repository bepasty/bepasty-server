# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

from .name import ItemName


def test_create():
    n = ItemName.create()
    assert n
