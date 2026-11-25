import os
import errno
from io import BytesIO
import time
import urllib

from flask import abort, current_app, jsonify, request, url_for
from flask.views import MethodView
from werkzeug.exceptions import BadRequest, Conflict, NotFound, Forbidden

from ..constants import COMPLETE, FILENAME, SIZE
from ..utils.date_funcs import get_maxlife
from ..utils.http import ContentRange, is_safe_external_url, redirect_next
from ..utils.name import ItemName
from ..utils.permissions import CREATE, may
from ..utils.upload import Upload, create_item, background_compute_hash


class UploadView(MethodView):
    def post(self):
        if not may(CREATE):
            raise Forbidden()
        f = request.files.get('file')
        t = request.form.get('text')
        # Note: "and f.filename" is needed due to a missing __bool__ method in
        # werkzeug.datastructures.FileStorage, to work around it crashing
        # on Python 3.x.
        if f and f.filename:
            # Check Content-Range, disallow its usage
            if ContentRange.from_request():
                abort(416)

            # Check Content-Type; default to application/octet-stream
            content_type = (
                f.headers.get('Content-Type') or
                request.headers.get('Content-Type'))
            content_type_hint = 'application/octet-stream'
            filename = f.filename

            # Get size of temporary file
            f.seek(0, os.SEEK_END)
            size = f.tell()
            f.seek(0)
        elif t is not None:
            # t is already Unicode, but we want UTF-8 for storage
            t = t.encode('utf-8')
            content_type = request.form.get('contenttype')  # TODO: add coding
            content_type_hint = 'text/plain'
            if content_type == 'text/x-bepasty-redirect' and not is_safe_external_url(t.decode('utf-8')):
                abort(400, description="Redirect URL must be an absolute http or https URL.")
            size = len(t)
            f = BytesIO(t)
            filename = request.form.get('filename')
        else:
            raise NotImplementedError
        # Set the maximum lifetime
        maxtime = get_maxlife(request.form, underscore=False)
        maxlife_timestamp = int(time.time()) + maxtime if maxtime > 0 else maxtime
        name = create_item(f, filename, size, content_type, content_type_hint, maxlife_stamp=maxlife_timestamp)
        kw = {}
        if filename:
            kw['_anchor'] = urllib.parse.quote(filename)
        if content_type == 'text/x-bepasty-redirect':
            # After creating a redirect, we want to stay on the Bepasty
            # redirect display so the user can copy the URL.
            kw['delay'] = '9999'
        return redirect_next('bepasty.display', name=name, **kw)


class UploadNewView(MethodView):
    def post(self):
        if not may(CREATE):
            raise Forbidden()

        data = request.get_json()

        data_filename = data['filename']
        data_size = int(data['size'])
        data_type = data['type']

        # Set the maximum lifetime
        maxtime = get_maxlife(data, underscore=True)
        maxlife_timestamp = int(time.time()) + maxtime if maxtime > 0 else maxtime

        name = ItemName.create(current_app.storage)
        with current_app.storage.create(name, data_size) as item:
            # Save metadata
            Upload.meta_new(item, data_size, data_filename, data_type,
                            'application/octet-stream', name, maxlife_stamp=maxlife_timestamp)

            return jsonify({'url': url_for('bepasty.upload_continue', name=name),
                            'name': name})


class UploadContinueView(MethodView):
    def post(self, name):
        if not may(CREATE):
            raise Forbidden()

        f = request.files['file']
        if not f:
            raise NotImplementedError

        # Check Content-Range
        content_range = ContentRange.from_request()

        try:
            item = current_app.storage.openwrite(name)
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise NotFound()
            raise

        with item:
            # Only an upload in progress (created by UploadNewView) may receive data.
            # Otherwise, anybody with "create" permission could overwrite the content
            # of any existing (complete, maybe even locked) item.
            if item.meta[COMPLETE]:
                raise Conflict(description='Upload already complete.')

            # Writes must stay within the size declared when the upload was created
            # (that size was checked against MAX_ALLOWED_FILE_SIZE).
            declared_size = item.meta[SIZE]

            if content_range:
                if content_range.complete != declared_size:
                    raise BadRequest(description='Content-Range length does not match the declared size.')
                # Note: we ignore the hash as it is only for one chunk, not for the whole upload.
                # Also, we cannot continue computing the hash as we can't save the internal
                # state of the hash object.
                size_written, _ = Upload.data(item, f, content_range.size, content_range.begin)
                file_hash = ''
                is_complete = content_range.is_complete

            else:
                # Get the size of the temporary file
                f.seek(0, os.SEEK_END)
                size = f.tell()
                f.seek(0)
                if size != declared_size:
                    raise BadRequest(description='Upload size does not match the declared size.')

                size_written, file_hash = Upload.data(item, f, size)
                is_complete = True

            if is_complete:
                Upload.meta_complete(item, file_hash)

            result = jsonify({'files': [{
                'name': name,
                'filename': item.meta[FILENAME],
                'size': item.meta[SIZE],
                'url': "{}#{}".format(url_for('bepasty.display', name=name), item.meta[FILENAME]),  # Anchor to filename
            }]})

        if is_complete and not file_hash:
            background_compute_hash(current_app.storage, name)

        return result


class UploadAbortView(MethodView):
    # This deletes data, so it must be POST: GET requests are not checked for CSRF.
    def post(self, name):
        if not may(CREATE):
            raise Forbidden()

        try:
            item = current_app.storage.open(name)
        except OSError as e:
            if e.errno == errno.ENOENT:
                return 'No file found.', 404
            raise

        if item.meta[COMPLETE]:
            error = 'Upload complete. Cannot delete file-upload garbage.'
        else:
            error = None
        if error:
            return error, 409

        try:
            item = current_app.storage.remove(name)
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise NotFound()
            raise
        return 'Upload aborted'
