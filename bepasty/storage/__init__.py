# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

import importlib


def create_storage(app):
    storage = importlib.import_module('.' + app.config['STORAGE'], __name__)
    return storage.Storage(app)
