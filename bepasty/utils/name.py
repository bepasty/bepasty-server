# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

import uuid

from werkzeug.routing import BaseConverter


class ItemName(str):
    def __new__(cls, uuid):
        return str(uuid)

    @classmethod
    def create(cls):
        return cls(uuid.uuid4())


class ItemNameConverter(BaseConverter):
    """
    Accept UUID like names.
    """
    regex = '[a-z0-9]{8}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{12}'
    weight = 200


def setup_werkzeug_routing(app):
    app.url_map.converters['itemname'] = ItemNameConverter
