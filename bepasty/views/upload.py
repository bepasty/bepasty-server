# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

import os
import errno
from StringIO import StringIO
import time

from flask import abort, current_app, jsonify, request, url_for
from flask.views import MethodView
from werkzeug.exceptions import NotFound, Forbidden
from werkzeug.urls import url_quote

from ..utils.http import ContentRange, redirect_next
from ..utils.name import ItemName
from ..utils.upload import Upload, create_item, background_compute_hash
from ..utils.permissions import *
from . import blueprint
from ..utils.date_funcs import time_unit_to_sec


class UploadView(MethodView):
    def post(self):
        if not may(CREATE):
            raise Forbidden()
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
            content_type_hint = 'application/octet-stream'
            filename = f.filename

            # Get size of temporary file
            f.seek(0, os.SEEK_END)
            size = f.tell()
            f.seek(0)
        elif t is not None:
            # t is already unicode, but we want utf-8 for storage
            t = t.encode('utf-8')
            content_type = request.form.get('contenttype')  # TODO: add coding
            content_type_hint = 'text/plain'
            size = len(t)
            f = StringIO(t)
            filename = request.form.get('filename')
        else:
            raise NotImplementedError
        # set max lifetime
        maxlife_unit = request.form.get('maxlife-unit', 'forever').upper()
        maxlife_value = int(request.form.get('maxlife-value', 1))
        maxtime = time_unit_to_sec(maxlife_value, maxlife_unit)
        maxlife_timestamp = int(time.time()) + maxtime if maxtime > 0 else maxtime
        name = create_item(f, filename, size, content_type, content_type_hint, maxlife_stamp=maxlife_timestamp)
        return redirect_next('bepasty.display', name=name, _anchor=url_quote(filename))


class UploadNewView(MethodView):
    def post(self):
        if not may(CREATE):
            raise Forbidden()

        data = request.get_json()

        data_filename = data['filename']
        data_size = int(data['size'])
        data_type = data['type']

        # set max lifetime
        maxlife_value = int(data['maxlife_value'])
        maxlife_unit = data['maxlife_unit'].upper()
        maxtime = time_unit_to_sec(maxlife_value, maxlife_unit)
        maxlife_timestamp = int(time.time()) + maxtime if maxtime > 0 else maxtime

        name = ItemName.create()
        with current_app.storage.create(name, data_size) as item:
            # Save meta-data
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
                'url': "{0}#{1}".format(url_for('bepasty.display', name=name),
                                        item.meta['filename']),
            }]})

        if is_complete and not file_hash:
            background_compute_hash(current_app.storage, name)

        return result


class UploadAbortView(MethodView):
    def get(self, name):
        if not may(CREATE):
            raise Forbidden()

        try:
            item = current_app.storage.open(name)
        except (OSError, IOError) as e:
            if e.errno == errno.ENOENT:
                return 'No file found.', 404
            raise

        if item.meta['complete']:
            error = 'Upload complete. Cannot delete fileupload garbage.'
        else:
            error = None
        if error:
            return error, 409

        try:
            item = current_app.storage.remove(name)
        except (OSError, IOError) as e:
            if e.errno == errno.ENOENT:
                raise NotFound()
            raise
        return 'Upload aborted'

blueprint.add_url_rule('/+upload', view_func=UploadView.as_view('upload'))
blueprint.add_url_rule('/+upload/new', view_func=UploadNewView.as_view('upload_new'))
blueprint.add_url_rule('/+upload/<itemname:name>', view_func=UploadContinueView.as_view('upload_continue'))
blueprint.add_url_rule('/+upload/<itemname:name>/abort', view_func=UploadAbortView.as_view('upload_abort'))
