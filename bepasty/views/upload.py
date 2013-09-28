# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

from flask import current_app, jsonify, redirect, request, url_for
from flask.views import MethodView

from ..utils.name import ItemName
from . import blueprint


class Upload(object):
    @staticmethod
    def upload():
        f = request.files['file']
        if not f:
            raise NotImplementedError

        n = ItemName.create()

        with current_app.storage.create(n) as item:
            # Copy data from temp file into storage
            offset = 0
            while True:
                buf = f.read(16*1024)
                if not buf:
                    break
                item.data.write(buf, offset)
                offset += len(buf)

            # Save meta-data
            item.meta['filename'] = f.filename
            item.meta['size'] = offset

            return n, {'filename': f.filename, 'size': offset, 'url': '/' + n}


class UploadView(MethodView):
    def post(self):
        n, info = Upload.upload()
        return redirect(url_for('bepasty.display', name=n))


class UploadNewView(MethodView):
    def post(self):
        data = request.get_json()
        data_filename = data['filename']
        data_size = data['size']
#        #data_type = data['type']

        n = ItemName.create()

        with current_app.storage.create(n) as item:
            # Save meta-data
            item.meta['filename'] = data_filename
            item.meta['size'] = data_size
#            item.meta['type'] = data_type

            return jsonify({'url': url_for('bepasty.upload_continue', name=n)})


class UploadContinueView(MethodView):
    def post(self, name):
        n = ItemName.parse(name)

        with current_app.storage.openwrite(n) as item:
            raise RuntimeError


blueprint.add_url_rule('/+upload', view_func=UploadView.as_view('upload'))
blueprint.add_url_rule('/+upload/new', view_func=UploadNewView.as_view('upload_new'))
blueprint.add_url_rule('/+upload/<name>', view_func=UploadContinueView.as_view('upload_continue'))
