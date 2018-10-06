import errno
import time

from flask import Response, current_app, render_template, stream_with_context
from flask.views import MethodView
from werkzeug.exceptions import NotFound, Forbidden

from ..constants import COMPLETE, FILENAME, LOCKED, SIZE, TIMESTAMP_DOWNLOAD, TYPE
from ..utils.date_funcs import delete_if_lifetime_over
from ..utils.permissions import ADMIN, READ, may


class DownloadView(MethodView):
    content_disposition = 'attachment'  # to trigger download

    def get(self, name):
        if not may(READ):
            raise Forbidden()
        try:
            item = current_app.storage.openwrite(name)
        except (OSError, IOError) as e:
            if e.errno == errno.ENOENT:
                raise NotFound()
            raise

        if not item.meta[COMPLETE]:
            error = 'Upload incomplete. Try again later.'
        else:
            error = None
        if error:
            try:
                return render_template('error.html', heading=item.meta[FILENAME], body=error), 409
            finally:
                item.close()

        if item.meta[LOCKED] and not may(ADMIN):
            raise Forbidden()

        if delete_if_lifetime_over(item, name):
            raise NotFound()

        def stream():
            with item as _item:
                # Stream content from storage
                offset = 0
                size = _item.data.size
                while offset < size:
                    buf = _item.data.read(16 * 1024, offset)
                    offset += len(buf)
                    yield buf
                item.meta[TIMESTAMP_DOWNLOAD] = int(time.time())

        ct = item.meta[TYPE]
        dispo = self.content_disposition
        if dispo != 'attachment':
            # no simple download, so we must be careful about XSS
            if ct.startswith("text/"):
                ct = 'text/plain'  # only send simple plain text

        ret = Response(stream_with_context(stream()))
        ret.headers['Content-Disposition'] = '{0}; filename="{1}"'.format(
            dispo, item.meta[FILENAME])
        ret.headers['Content-Length'] = item.meta[SIZE]
        ret.headers['Content-Type'] = ct
        ret.headers['X-Content-Type-Options'] = 'nosniff'  # yes, we really mean it
        return ret


class InlineView(DownloadView):
    content_disposition = 'inline'  # to trigger viewing in browser, for some types
