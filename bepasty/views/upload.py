# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

import os
import re
import time
import hashlib
from StringIO import StringIO

from flask import abort, current_app, jsonify, redirect, request, url_for, session
from flask.views import MethodView

from ..utils.http import ContentRange
from ..utils.name import ItemName
from . import blueprint


class Upload(object):
    _filename_re = re.compile(r'[^a-zA-Z0-9 \*+:;.,_-]+')
    _type_re = re.compile(r'[^a-zA-Z0-9/+.-]+')

    @classmethod
    def filter_size(cls, i):
        """
        Filter size.
        Check for advertised size.
        """
        i = int(i)
        if i >= 4 * 1024 * 1024 * 1024:  # 4 GiB
            abort(413)
        return i

    @classmethod
    def filter_filename(cls, i):
        """
        Filter filename.
        Only allow some basic characters and shorten to 50 characters.
        """
        return cls._filename_re.sub('', i)[:50]

    @classmethod
    def filter_type(cls, i):
        """
        Filter Content-Type
        Only allow some basic characters and shorten to 50 characters.
        """
        if not i:
            return 'application/octet-stream'
        return cls._type_re.sub('', i)[:50]

    @classmethod
    def meta_new(cls, item, input_size, input_filename, input_type):
        item.meta['filename'] = cls.filter_filename(input_filename)
        item.meta['size'] = cls.filter_size(input_size)
        item.meta['type'] = cls.filter_type(input_type)
        item.meta['timestamp-upload'] = int(time.time())
        item.meta['complete'] = False

        item.meta['unlocked'] = current_app.config['UPLOAD_UNLOCKED']

    @classmethod
    def meta_complete(cls, item, file_hash):
        item.meta['complete'] = True
        item.meta['hash'] = file_hash

    @staticmethod
    def data(item, f, size_input, offset=0):
        """
        Copy data from temp file into storage.
        """
        read_length = 16 * 1024
        size_written = 0
        hasher = hashlib.sha256()

        while True:
            read_length = min(read_length, size_input)
            if size_input == 0:
                break

            buf = f.read(read_length)
            if not buf:
                # Should not happen, we already checked the size
                raise RuntimeError

            item.data.write(buf, offset + size_written)
            hasher.update(buf)

            len_buf = len(buf)
            size_written += len_buf
            size_input -= len_buf

        return size_written, hasher.hexdigest()


def check_upload_permission():
    if not session.get('may_upload', False):
        abort(403)


class UploadView(MethodView):
    def post(self):
        check_upload_permission()

        f = request.files['file']
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
            content_type = 'text/plain'  # TODO: add coding
            size = len(t)
            f = StringIO(t)
            filename = 'paste.txt'  # TODO: remove filename requirement
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
        check_upload_permission()

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
        check_upload_permission()

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

                if content_range.is_complete:
                    Upload.meta_complete(item, '')
            else:
                # Get size of temporary file
                f.seek(0, os.SEEK_END)
                size = f.tell()
                f.seek(0)

                size_written, file_hash = Upload.data(item, f, size)
                Upload.meta_complete(item, file_hash)

            return jsonify({'files': [{
                'filename': item.meta['filename'],
                'size': item.meta['size'],
                'url': url_for('bepasty.display', name=name),
            }]})


class UploadAbortView(MethodView):
    def get(self, name):
        check_upload_permission()

        try:
            item = current_app.storage.open(name)
        except (OSError, IOError) as e:
            if e.errno == errno.ENOENT:
                return 'No file found.', 404

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
