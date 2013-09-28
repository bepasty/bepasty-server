# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

import collections

from flask import abort, current_app, jsonify, redirect, request, url_for
from flask.views import MethodView

from ..utils.name import ItemName
from . import blueprint


class ContentRange(collections.namedtuple('ContentRange', ('begin', 'end', 'complete'))):
    __slots__ = ()

    @classmethod
    def parse(cls, content_range):
        """
        Parse Content-Range header.
        Format is "bytes 0-524287/2000000".
        """
        range_type, range_count = content_range.split(' ', 1)
        # There are no other types then "bytes"
        if range_type != 'bytes':
            raise RuntimeError

        range_count, range_complete = range_count.split('/', 1)
        range_begin, range_end = range_count.split('-', 1)

        range_begin = int(range_begin)
        range_end = int(range_end)
        range_complete = int(range_complete)

        if range_begin <= range_end and range_end < range_complete:
            return ContentRange(range_begin, range_end, range_complete)
        raise RuntimeError

    @classmethod
    def from_request(cls):
        content_range = request.headers.get('Content-Range')
        if content_range is not None:
            return cls.parse(content_range)

    @property
    def size(self):
        return self.end - self.begin + 1


class Upload(object):
    @staticmethod
    def upload(item, f, offset=0):
        # Copy data from temp file into storage
        while True:
            buf = f.read(16*1024)
            if not buf:
                break
            item.data.write(buf, offset)
            offset += len(buf)

        return offset


class UploadView(MethodView):
    def post(self):
        f = request.files['file']
        if not f:
            raise NotImplementedError

        name = ItemName.create()

        with current_app.storage.create(name) as item:
            size = Upload.upload(item, f)

            # Save meta-data
            item.meta['filename'] = f.filename
            item.meta['size'] = size
#            item.meta['type'] = data_type

        return redirect(url_for('bepasty.display', name=name))


class UploadNewView(MethodView):
    def post(self):
        data = request.get_json()
        data_filename = data['filename']
        data_size = data['size']
#        #data_type = data['type']

        name = ItemName.create()

        with current_app.storage.create(name) as item:
            # Save meta-data
            item.meta['filename'] = data_filename
            item.meta['size'] = data_size
#            item.meta['type'] = data_type

            return jsonify({'url': url_for('bepasty.upload_continue', name=name)})


class UploadContinueView(MethodView):
    def post(self, name):
        name = ItemName.parse(name)

        with current_app.storage.openwrite(name) as item:
            raise RuntimeError


blueprint.add_url_rule('/+upload', view_func=UploadView.as_view('upload'))
blueprint.add_url_rule('/+upload/new', view_func=UploadNewView.as_view('upload_new'))
blueprint.add_url_rule('/+upload/<name>', view_func=UploadContinueView.as_view('upload_continue'))
