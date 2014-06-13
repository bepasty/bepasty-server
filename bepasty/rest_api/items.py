import hashlib
import os
import base64
import time
from io import BytesIO

from . import rest_api
from flask.views import MethodView
from flask import request, make_response, current_app, url_for, jsonify

from ..utils.name import ItemName
from ..utils.http import ContentRange
from ..views.upload import Upload


class ItemsView(MethodView):

    def post(self):
        file_type = request.headers.get("Content-Type")
        file_size = request.headers.get("Content-Length")
        file_name = request.headers.get("Content-Filename")

        Upload.filter_size(file_size)

        if not request.headers.get("Transaction-Id"):
            name = ItemName.create()
            item = current_app.storage.create(name, 0)

            item.meta["filename"] = Upload.filter_filename(file_name)
            item.meta["timestamp"] = int(time.time())
            item.meta['type'] = Upload.filter_type(file_type)

        else:
            name = base64.b64decode(request.headers.get("Transaction-Id"))
            item = current_app.storage.open(name)

        Upload.filter_size(item.data.size)

        if not request.headers.get("Content-Range"):
            return 'Content-Range not specified', 400

        file_range = ContentRange.from_request()

        raw_data = base64.b64decode(request.data)
        file_data = BytesIO(raw_data)

        Upload.data(item, file_data, len(raw_data), file_range.begin)

        response = make_response()
        response.headers["Transaction-Id"] = base64.b64encode(name)
        response.status = '200'

        if file_range.is_complete:
            item.meta['complete'] = True
            item.meta['unlocked'] = current_app.config['UPLOAD_UNLOCKED']
            item.meta['size'] = item.data.size
            response.status = '201'
            response.headers["Content-Location"] = url_for('bepasty_rest.items_detail', name=name)

        item.__exit__()
        return response


class ItemDetailView(MethodView):
    def get(self, name):
        with current_app.storage.open(name) as item:
            return jsonify({'uri': url_for('bepasty_rest.items_detail', name=name),
                            'file-meta': dict(item.meta)})

rest_api.add_url_rule('/items', view_func=ItemsView.as_view('items'))
rest_api.add_url_rule('/items/<itemname:name>', view_func=ItemDetailView.as_view('items_detail'))
#rest_api.add_url_rule('/items/<itemname:name>/data', view_func=ItemsDataView.as_view('items_data'))
#rest_api.add_url_rule('/items/<itemname:name>/meta', view_func=ItemsMetaView.as_view('items_meta')
