# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

from flask import Response, current_app, stream_with_context
from flask.views import MethodView

from ..utils.name import ItemName
from . import blueprint


class DownloadView(MethodView):
    def get(self, name):
        n = ItemName.parse(name)

        item = current_app.storage.open(n)

        def stream():
            try:
                # Stream content from storage
                offset = 0
                size = item.data.size
                while offset < size:
                    buf = item.data.read(16*1024, offset)
                    offset += len(buf)
                    yield buf
            finally:
                item.close()

        ret = Response(stream_with_context(stream()))
        ret.headers['Content-Disposition'] = 'attachment; filename="{}"'.format(item.meta['filename'])
        ret.headers['Content-Length'] = item.meta['size']
        return ret


blueprint.add_url_rule('/<name>/+download', view_func=DownloadView.as_view('download'))
