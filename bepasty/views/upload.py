from flask import current_app, redirect, request, url_for
from flask.views import MethodView

from ..utils.name import ItemName
from . import blueprint


class UploadView(MethodView):
    def get(self):
        raise NotImplementedError

    def post(self):
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

        return redirect(url_for('bepasty.display', name=n))


blueprint.add_url_rule('/+upload', view_func=UploadView.as_view('upload'))
