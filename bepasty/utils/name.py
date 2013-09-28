# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

import uuid


class ItemName(str):
    def __new__(self, uuid):
        return str(uuid)

    @classmethod
    def create(cls):
        return cls(uuid.uuid4())

    @classmethod
    def parse(cls, s):
        return cls(uuid.UUID(s))
