# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

import os

from flask import abort, current_app, jsonify, redirect, request, url_for
from flask.views import MethodView

from ..utils.html import ContentRange
from ..utils.name import ItemName
from . import blueprint


class Upload(object):
    @staticmethod
    def upload(item, f, size_input, offset=0):
        """
        Copy data from temp file into storage.
        """
        read_length = 16*1024
        size_written = 0

        while True:
            read_length = min(read_length, size_input)
            if size_input == 0:
                break

            buf = f.read(read_length)
            if not buf:
                break

            item.data.write(buf, offset + size_written)

            len_buf = len(buf)
            size_written += len_buf
            size_input -= len_buf

        return size_written


class UploadView(MethodView):
    def post(self):
        f = request.files['file']
        if not f:
            raise NotImplementedError

        # Check Content-Range, disallow its usage
        if ContentRange.from_request():
            abort(416)

        # Check Content-Type, default to application/octet-stream
        content_type = request.headers.get('Content-Type') or 'application/octet-stream'

        # Get size of temporary file
        f.seek(0, os.SEEK_END)
        size = f.tell()
        f.seek(0)

        # Create new name
        name = ItemName.create()

        with current_app.storage.create(name, size) as item:
            Upload.upload(item, f, size)

            # Save meta-data
            item.meta['filename'] = f.filename
            item.meta['size'] = size
            item.meta['type'] = content_type

        return redirect(url_for('bepasty.display', name=name))


class UploadNewView(MethodView):
    def post(self):
        data = request.get_json()
        data_filename = data['filename']
        data_size = data['size']
        data_type = data['type']

        # Create new name
        name = ItemName.create()

        with current_app.storage.create(name, data_size) as item:
            # Save meta-data
            item.meta['filename'] = data_filename
            item.meta['size'] = data_size
            item.meta['type'] = data_type

            return jsonify({'url': url_for('bepasty.upload_continue', name=name)})


class UploadContinueView(MethodView):
    def post(self, name):
        f = request.files['file']
        if not f:
            raise NotImplementedError

        # Check Content-Range
        content_range = ContentRange.from_request()

        # Parse name
        name = ItemName.parse(name)

        with current_app.storage.openwrite(name) as item:
            if content_range:
                Upload.upload(item, f, content_range.size, content_range.begin)
            else:
                # Get size of temporary file
                f.seek(0, os.SEEK_END)
                size = f.tell()
                f.seek(0)

                Upload.upload(item, f, size)

            return jsonify({'files': [{
                'filename': item.meta['filename'],
                'size': item.meta['size'],
                'url': url_for('bepasty.display', name=name),
            }]})


blueprint.add_url_rule('/+upload', view_func=UploadView.as_view('upload'))
blueprint.add_url_rule('/+upload/new', view_func=UploadNewView.as_view('upload_new'))
blueprint.add_url_rule('/+upload/<name>', view_func=UploadContinueView.as_view('upload_continue'))
