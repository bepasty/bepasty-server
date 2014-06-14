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
        """
        Upload file via REST-API. Chunked Upload is supported.

        HTTP Headers that need to be given:
        * Content-Type: The type of the file that is being uploaded. If this is not given filetype will be 'application/octet-stream'
        * Content-Length: The total size of the file to be uploaded.
        * Content-Filename: The filename of the file. This will be shown when downloading.
        * Content-Range: The Content-Range of the Chunk that is currently being uploaded. Follows the HTTP-Header Specifications.
        * Transaction-Id: The Transaction-Id for Chunked Uploads. Needs to be delivered when uploading in chunks (After the first chunk).

        To start an upload, the HTTP Headers need to be delivered. The body of the request needs to be the base64 encoded file contents
        that is uploaded. Content-Length is the original file size before base64 encoding. Content-Range follows the same logic.
        After the first chunk is uploaded, bepasty will return the Transaction-Id to continue the upload. Deliver the Transaction-Id and
        the correct Content-Range to continue upload. After the file is completely uploaded, the file will be marked
        as complete and a 201 HTTP Status will be returned. The Content-Location Header will contain the api url to the uploaded Item.

        If the file size exceeds the permitted size, the upload will be aborted. This will be checked twice.
        The first check is the provided Content-Length. The second is the actual file size on the server.
        """
        file_type = request.headers.get("Content-Type")
        file_size = request.headers.get("Content-Length")
        file_name = request.headers.get("Content-Filename")

        Upload.filter_size(file_size)

        if not request.headers.get("Transaction-Id"):
            name = ItemName.create()
            item = current_app.storage.create(name, 0)

            item.meta['filename'] = Upload.filter_filename(file_name)
            item.meta['timestamp'] = int(time.time())
            item.meta['type'] = Upload.filter_type(file_type)

        else:
            name = base64.b64decode(request.headers.get("Transaction-Id"))
            item = current_app.storage.openwrite(name)

        Upload.filter_size(item.data.size)

        if not request.headers.get("Content-Range"):
            return 'Content-Range not specified', 400

        file_range = ContentRange.from_request()
        if not item.data.size == file_range.begin:
            return ('Content-Range inconsistent. Last byte: %d' % item.data.size), 409

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
