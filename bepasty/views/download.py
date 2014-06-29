# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

import errno
import time

from flask import Response, current_app, render_template, stream_with_context, abort
from flask.views import MethodView
from werkzeug.exceptions import NotFound

from ..utils.name import ItemName
from ..utils.permissions import *
from . import blueprint


class DownloadView(MethodView):
    content_disposition = 'attachment'  # to trigger download

    def get(self, name):
        if not may(READ):
            abort(403)
        try:
            item = current_app.storage.openwrite(name)
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise NotFound()
            raise

        if not item.meta.get('complete'):
            error = 'Upload incomplete. Try again later.'
        else:
            error = None
        if error:
            try:
                return render_template('display_error.html', name=name, item=item, error=error), 409
            finally:
                item.close()

        if item.meta.get('locked') and not may(ADMIN):
            abort(403)

        def stream():
            with item as _item:
                # Stream content from storage
                offset = 0
                size = _item.data.size
                while offset < size:
                    buf = _item.data.read(16 * 1024, offset)
                    offset += len(buf)
                    yield buf
                item.meta['timestamp-download'] = int(time.time())

        ret = Response(stream_with_context(stream()))
        ret.headers['Content-Disposition'] = '{}; filename="{}"'.format(
            self.content_disposition, item.meta['filename'])
        ret.headers['Content-Length'] = item.meta['size']
        ret.headers['Content-Type'] = item.meta['type']  # 'application/octet-stream'
        return ret


class InlineView(DownloadView):
    content_disposition = 'inline'  # to trigger viewing in browser, for some types


blueprint.add_url_rule('/<itemname:name>/+download', view_func=DownloadView.as_view('download'))
blueprint.add_url_rule('/<itemname:name>/+inline', view_func=InlineView.as_view('inline'))
