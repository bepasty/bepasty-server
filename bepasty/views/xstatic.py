from ..bepasty_xstatic import serve_files

from flask import Response, abort
from flask import send_from_directory

from . import blueprint

@blueprint.route('/xstatic/<name>', defaults=dict(filename=''))
@blueprint.route('/xstatic/<name>/<path:filename>')
def xstatic(name, filename):
    '''Route to serve the xstatic files (from serve_files)'''
    print 'YEAHHHH > xstatic > name=%s filename=%s' % (name, filename)
    try:
        base_path = serve_files[name]
    except KeyError:
        abort(404)

    if not filename:
        abort(404)

    return send_from_directory(base_path, filename)
