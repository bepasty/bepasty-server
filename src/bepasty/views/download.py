import errno
from io import BytesIO
import os
import time

try:
    import PIL
except ImportError:
    # Pillow / PIL is optional
    PIL = None
else:
    from PIL import Image

from flask import Response, current_app, render_template, stream_with_context
from flask.views import MethodView
from werkzeug.exceptions import NotFound, Forbidden

from ..constants import COMPLETE, FILENAME, LOCKED, SIZE, TIMESTAMP_DOWNLOAD, TYPE
from ..utils.date_funcs import delete_if_lifetime_over
from ..utils.permissions import ADMIN, READ, may


class DownloadView(MethodView):
    content_disposition = 'attachment'  # to trigger download

    def err_incomplete(self, item, error):
        return render_template('error.html', heading=item.meta[FILENAME], body=error), 409

    def stream(self, item, start, limit):
        with item as _item:
            # Stream content from storage
            offset = max(0, start)
            while offset < limit:
                buf = _item.data.read(min(limit - offset, 16 * 1024), offset)
                offset += len(buf)
                yield buf
            item.meta[TIMESTAMP_DOWNLOAD] = int(time.time())

    def response(self, item, name):
        ct = item.meta[TYPE]
        dispo = self.content_disposition
        if dispo != 'attachment':
            # no simple download, so we must be careful about XSS
            if ct.startswith("text/"):
                ct = 'text/plain'  # only send simple plain text

        ret = Response(stream_with_context(self.stream(item, 0, item.data.size)))
        ret.headers['Content-Disposition'] = '{}; filename="{}"'.format(
            dispo, item.meta[FILENAME])
        ret.headers['Content-Length'] = item.meta[SIZE]
        ret.headers['Content-Type'] = ct
        ret.headers['X-Content-Type-Options'] = 'nosniff'  # yes, we really mean it
        return ret

    def get(self, name):
        if not may(READ):
            raise Forbidden()
        try:
            item = current_app.storage.openwrite(name)
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise NotFound()
            raise

        try:
            need_close = True
            if not item.meta[COMPLETE]:
                return self.err_incomplete(item, 'Upload incomplete. Try again later.')

            if item.meta[LOCKED] and not may(ADMIN):
                raise Forbidden()

            if delete_if_lifetime_over(item, name):
                raise NotFound()
            need_close = False
        finally:
            if need_close:
                item.close()

        return self.response(item, name)


class InlineView(DownloadView):
    content_disposition = 'inline'  # to trigger viewing in browser, for some types


class ThumbnailView(InlineView):
    thumbnail_size = 192, 108
    thumbnail_data = """\
        <?xml version="1.0" encoding="UTF-8" standalone="no"?>
        <svg width="108" height="108" viewBox="0 0 108 108" xmlns="http://www.w3.org/2000/svg">
        <rect x="1" y="1" width="106" height="106" fill="whitesmoke" stroke-width="2" stroke="blue" />
            <line x1="1" y1="1" x2="106" y2="106" stroke="blue" stroke-width="2" />
            <line x1="1" y1="106" x2="106" y2="0" stroke="blue" stroke-width="2" />
        </svg>""".strip().encode()

    def err_incomplete(self, item, error):
        return b'', 409  # conflict

    def response(self, item, name):
        sz = item.meta[SIZE]
        fn = item.meta[FILENAME]
        ct = item.meta[TYPE]
        unsupported = PIL is None or ct not in {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}
        if unsupported:
            # return a placeholder thumbnail for unsupported item types
            ret = Response(self.thumbnail_data)
            ret.headers['Content-Length'] = len(self.thumbnail_data)
            ret.headers['Content-Type'] = 'image/svg+xml'
            ret.headers['X-Content-Type-Options'] = 'nosniff'  # yes, we really mean it
            return ret

        if ct in ('image/jpeg', ):
            thumbnail_type = 'jpeg'
        elif ct in ('image/png', 'image/gif'):
            thumbnail_type = 'png'
        elif ct in ('image/webp', ):
            thumbnail_type = 'webp'
        else:
            raise ValueError('unrecognized image content type')

        # compute thumbnail data "on the fly"
        with BytesIO(item.data.read(sz, 0)) as img_bio, BytesIO() as thumbnail_bio:
            with Image.open(img_bio) as img:
                img.thumbnail(self.thumbnail_size)
                img.save(thumbnail_bio, thumbnail_type)
            thumbnail_data = thumbnail_bio.getvalue()

        name, ext = os.path.splitext(fn)
        thumbnail_fn = '{}-thumb.{}'.format(name, thumbnail_type)

        ret = Response(thumbnail_data)
        ret.headers['Content-Disposition'] = '{}; filename="{}"'.format(
            self.content_disposition, thumbnail_fn)
        ret.headers['Content-Length'] = len(thumbnail_data)
        ret.headers['Content-Type'] = 'image/%s' % thumbnail_type
        ret.headers['X-Content-Type-Options'] = 'nosniff'  # yes, we really mean it
        return ret
