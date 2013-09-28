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

            # Save filename
            item.meta['filename'] = f.filename
            item.meta['size'] = offset

            return n, {'filename': f.filename, 'size': offset, 'url': '/' + n}


class UploadView(MethodView):
    def post(self):
        n, info = Upload.upload()
        return redirect(url_for('bepasty.display', name=n))


class UploadViewJson(MethodView):
    def post(self):
        n, info = Upload.upload()
        return jsonify({'files': [info]})


blueprint.add_url_rule('/+upload', view_func=UploadView.as_view('upload'))
blueprint.add_url_rule('/+upload/json', view_func=UploadViewJson.as_view('upload_json'))
