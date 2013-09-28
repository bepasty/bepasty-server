# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

def create_storage(app):
    # XXX
    from .filesystem import Storage
    app.storage = Storage('/tmp/bepasty')

