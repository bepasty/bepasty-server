# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

from flask import Response, current_app, render_template, stream_with_context
from flask.views import MethodView

from ..utils.name import ItemName
from . import blueprint


class DownloadView(MethodView):
    def get(self, name):
        baseitem = current_app.storage.open(name)

        if not baseitem.meta['complete']:
            error = 'Upload incomplete. Try again later.'
            return render_template('display_error.html', name=name, item=baseitem, error=error), 409

        def stream():
            with baseitem as item:
                # Stream content from storage
                offset = 0
                size = item.data.size
                while offset < size:
                    buf = item.data.read(16*1024, offset)
                    offset += len(buf)
                    yield buf

        ret = Response(stream_with_context(stream()))
        ret.headers['Content-Disposition'] = 'attachment; filename="{}"'.format(baseitem.meta['filename'])
        ret.headers['Content-Length'] = baseitem.meta['size']
        return ret


blueprint.add_url_rule('/<itemname:name>/+download', view_func=DownloadView.as_view('download'))
