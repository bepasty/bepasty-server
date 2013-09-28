def create_storage(app):
    # XXX
    from .filesystem import Storage
    app.storage = Storage('/tmp/bepasty')

