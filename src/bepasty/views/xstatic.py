from flask import send_from_directory
from werkzeug.exceptions import NotFound

from ..bepasty_xstatic import serve_files


def xstatic(name, filename):
    """Route to serve the xstatic files (from serve_files)"""
    try:
        base_path = serve_files[name]
    except KeyError:
        raise NotFound()

    if not filename:
        raise NotFound()

    return send_from_directory(base_path, filename)
