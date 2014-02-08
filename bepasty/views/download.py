# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

import errno

from flask import Response, current_app, render_template, stream_with_context
from flask.views import MethodView
from werkzeug.exceptions import NotFound

from ..utils.name import ItemName
from . import blueprint


class DownloadView(MethodView):
    def get(self, name):
        try:
            item = current_app.storage.open(name)
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise NotFound()
            # XXX item is undefined here, but we proceed... XXX

        if not item.meta.get('unlocked'):
            error = 'File Locked.'
        elif not item.meta.get('complete'):
            error = 'Upload incomplete. Try again later.'
        else:
            error = None
        if error:
            try:
                return render_template('display_error.html', name=name, item=item, error=error), 409
            finally:
                item.close()

        def stream():
            with item as _item:
                # Stream content from storage
                offset = 0
                size = _item.data.size
                while offset < size:
                    buf = _item.data.read(16 * 1024, offset)
                    offset += len(buf)
                    yield buf

        ret = Response(stream_with_context(stream()))
        ret.headers['Content-Disposition'] = 'attachment; filename="{}"'.format(item.meta['filename'])
        ret.headers['Content-Length'] = item.meta['size']
        ret.headers['Content-Type'] = item.meta['type']  # 'application/octet-stream'
        return ret


blueprint.add_url_rule('/<itemname:name>/+download', view_func=DownloadView.as_view('download'))
