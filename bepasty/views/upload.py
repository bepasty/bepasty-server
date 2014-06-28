# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

import os
import errno
from StringIO import StringIO

from flask import abort, current_app, jsonify, redirect, request, url_for, session, render_template, abort
from flask.views import MethodView

from ..utils.http import ContentRange
from ..utils.name import ItemName
from ..utils.upload import Upload, background_compute_hash
from ..utils.permissions import *
from . import blueprint


class UploadView(MethodView):
    def post(self):
        if not may(CREATE):
            abort(403)
        f = request.files.get('file')
        t = request.form.get('text')
        if f:
            # Check Content-Range, disallow its usage
            if ContentRange.from_request():
                abort(416)

            # Check Content-Type, default to application/octet-stream
            content_type = (
                f.headers.get('Content-Type') or
                request.headers.get('Content-Type'))
            filename = f.filename

            # Get size of temporary file
            f.seek(0, os.SEEK_END)
            size = f.tell()
            f.seek(0)
        elif t is not None:
            # t is already unicode, but we want utf-8 for storage
            t = t.encode('utf-8')
            content_type = request.form.get('contenttype') or 'text/plain'  # TODO: add coding
            size = len(t)
            f = StringIO(t)
            filename = request.form.get('filename') or 'paste.txt'
        else:
            raise NotImplementedError

        # Create new name
        name = ItemName.create()

        with current_app.storage.create(name, size) as item:
            size_written, file_hash = Upload.data(item, f, size)
            Upload.meta_new(item, size, filename, content_type)
            Upload.meta_complete(item, file_hash)

        return redirect(url_for('bepasty.display', name=name))


class UploadNewView(MethodView):
    def post(self):
        if not may(CREATE):
            abort(403)

        data = request.get_json()

        data_filename = data['filename']
        data_size = int(data['size'])
        data_type = data['type']

        # Create new name
        name = ItemName.create()

        with current_app.storage.create(name, data_size) as item:
            # Save meta-data
            Upload.meta_new(item, data_size, data_filename, data_type)

            return jsonify({'url': url_for('bepasty.upload_continue', name=name),
                            'name': name})


class UploadContinueView(MethodView):
    def post(self, name):
        if not may(CREATE):
            abort(403)

        f = request.files['file']
        if not f:
            raise NotImplementedError

        # Check Content-Range
        content_range = ContentRange.from_request()

        with current_app.storage.openwrite(name) as item:
            if content_range:
                # note: we ignore the hash as it is only for 1 chunk, not for the whole upload.
                # also, we can not continue computing the hash as we can't save the internal
                # state of the hash object
                size_written, _ = Upload.data(item, f, content_range.size, content_range.begin)
                file_hash = ''
                is_complete = content_range.is_complete

            else:
                # Get size of temporary file
                f.seek(0, os.SEEK_END)
                size = f.tell()
                f.seek(0)

                size_written, file_hash = Upload.data(item, f, size)
                is_complete = True

            if is_complete:
                Upload.meta_complete(item, file_hash)

            result = jsonify({'files': [{
                'name': name,
                'filename': item.meta['filename'],
                'size': item.meta['size'],
                'url': url_for('bepasty.display', name=name),
            }]})

        if is_complete and not file_hash:
            background_compute_hash(current_app.storage, name)

        return result


class UploadAbortView(MethodView):
    def get(self, name):
        if not may(CREATE):
            abort(403)

        try:
            item = current_app.storage.open(name)
        except (OSError, IOError) as e:
            if e.errno == errno.ENOENT:
                return 'No file found.', 404
            raise

        if item.meta.get('complete'):
            error = 'Upload complete. Cannot delete fileupload garbage.'
        else:
            error = None
        if error:
            return error, 409

        try:
            item = current_app.storage.remove(name)
        except (OSError, IOError) as e:
            if e.errno == errno.ENOENT:
                return render_template('file_not_found.html'), 404
        return 'Upload aborted'

blueprint.add_url_rule('/+upload', view_func=UploadView.as_view('upload'))
blueprint.add_url_rule('/+upload/new', view_func=UploadNewView.as_view('upload_new'))
blueprint.add_url_rule('/+upload/<itemname:name>', view_func=UploadContinueView.as_view('upload_continue'))
blueprint.add_url_rule('/+upload/<itemname:name>/abort', view_func=UploadAbortView.as_view('upload_abort'))
