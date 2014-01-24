# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

import importlib


def create_storage(app):
    """
    Load specified storage and return the object.
    """
    if 'STORAGE' not in app.config:
        raise Exception("Missing STORAGE config key")

    storage = importlib.import_module('.' + app.config['STORAGE'], __name__)
    return storage.Storage(app)
