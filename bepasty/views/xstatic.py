from ..bepasty_xstatic import serve_files

from flask import Response, abort
from flask import send_from_directory
from werkzeug.exceptions import NotFound

from . import blueprint


@blueprint.route('/xstatic/<name>', defaults=dict(filename=''))
@blueprint.route('/xstatic/<name>/<path:filename>')
def xstatic(name, filename):
    """Route to serve the xstatic files (from serve_files)"""
    try:
        base_path = serve_files[name]
    except KeyError:
        raise NotFound()

    if not filename:
        raise NotFound()

    return send_from_directory(base_path, filename)
