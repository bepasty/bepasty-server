import base64
import time
from io import BytesIO

from flask import Response, make_response, url_for, jsonify, stream_with_context, request, current_app
from flask.views import MethodView
from werkzeug.exceptions import HTTPException, Conflict, InternalServerError, MethodNotAllowed

from ..constants import FILENAME, ID, SIZE, TYPE, TRANSACTION_ID
from ..utils._compat import bytes_type
from ..utils.date_funcs import get_maxlife
from ..utils.http import ContentRange, DownloadRange
from ..utils.name import ItemName
from ..utils.permissions import CREATE, LIST, may
from ..utils.upload import Upload, background_compute_hash
from ..views.filelist import file_infos
from ..views.download import DownloadView


# This wrapper to handle exception of REST api.
# @blueprint.add_errorhandler decorator can do it though. We have
# "/lodgeit/" in same blueprint, and didn't find the way to exclude
# "/lodgeit/" from add_errorhandler to handle exception as web site,
# not REST api.
def rest_errorhandler(func):
    def error_message(description, code):
        # maybe better to return error as json?
        return description, code

    def handler(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except HTTPException as e:
            return error_message(e.description, e.code)
        except Exception:
            if current_app.propagate_exceptions:
                # if testing/debug mode, re-raise
                raise
            exc = InternalServerError()
            return error_message(exc.description, exc.code)

    return handler


# Default handlers for REST api to handle error
class RestBase(MethodView):
    @rest_errorhandler
    def get(self, *args, **kwargs):
        raise MethodNotAllowed()

    @rest_errorhandler
    def post(self, *args, **kwargs):
        raise MethodNotAllowed()


class ItemUploadView(RestBase):
    @rest_errorhandler
    def post(self):
        """
        Upload file via REST-API. Chunked Upload is supported.

        HTTP Headers that need to be given:
        * Content-Type: The type of the file that is being uploaded.
            If this is not given filetype will be 'application/octet-stream'
        * Content-Length: The total size of the file to be uploaded.
        * Content-Filename: The filename of the file. This will be used when downloading.
        * Content-Range: The Content-Range of the Chunk that is currently being uploaded.
            Follows the HTTP-Header Specifications.
        * Transaction-ID: The Transaction-ID for Chunked Uploads.
            Needs to be delivered when uploading in chunks (after the first chunk).

        To start an upload, the HTTP Headers need to be delivered.
        The body of the request needs to be the base64 encoded file contents.
        Content-Length is the original file size before base64 encoding.
        Content-Range follows the same logic.
        After the first chunk is uploaded, bepasty will return the Transaction-ID to continue the upload.
        Deliver the Transaction-ID and the correct Content-Range to continue upload.
        After the file is completely uploaded, the file will be marked as complete and
        a 201 HTTP Status will be returned.
        The Content-Location Header will contain the api url to the uploaded Item.

        If the file size exceeds the permitted size, the upload will be aborted. This will be checked twice.
        The first check is the provided Content-Length. The second is the actual file size on the server.
        """
        if not may(CREATE):
            return 'Missing Permissions', 403

        # Collect all expected data from the Request
        file_type = request.headers.get("Content-Type")
        file_size = request.headers.get("Content-Length")
        file_name = request.headers.get("Content-Filename")

        # Check the file size from Request
        Upload.filter_size(file_size)

        # Check if Transaction-ID is available for continued upload
        if not request.headers.get(TRANSACTION_ID):
            # Create ItemName and empty file in Storage
            name = ItemName.create(current_app.storage)
            item = current_app.storage.create(name, 0)

            # set max lifetime
            maxtime = get_maxlife(request.headers, underscore=False)
            maxlife_timestamp = int(time.time()) + maxtime if maxtime > 0 else maxtime
            # Fill meta with data from Request
            Upload.meta_new(item, 0, file_name, file_type,
                            'application/octet-stream',
                            name, maxlife_stamp=maxlife_timestamp)
        else:
            # Get file name from Transaction-ID and open from Storage
            trans_id_s = request.headers.get(TRANSACTION_ID)
            trans_id_b = trans_id_s if isinstance(trans_id_s, bytes_type) else trans_id_s.encode()
            name_b = base64.b64decode(trans_id_b)
            name = name_b if isinstance(name_b, str) else name_b.decode()
            item = current_app.storage.openwrite(name)

        # Check the actual size of the file on the server against limit
        # Either 0 if new file or n bytes of already uploaded file
        Upload.filter_size(item.data.size)

        # Check Content-Range. Needs to be specified, even if only one chunk
        if not request.headers.get("Content-Range"):
            return 'Content-Range not specified', 400

        # Get Content-Range and check if Range is consistent with server state
        file_range = ContentRange.from_request()
        if not item.data.size == file_range.begin:
            return ('Content-Range inconsistent. Last byte on Server: %d' % item.data.size), 409

        # Decode Base64 encoded request data
        raw_data = base64.b64decode(request.data)
        file_data = BytesIO(raw_data)

        # Write data chunk to item
        Upload.data(item, file_data, len(raw_data), file_range.begin)

        # Make a Response and create Transaction-ID from ItemName
        response = make_response()
        name_b = name if isinstance(name, bytes_type) else name.encode()
        trans_id_b = base64.b64encode(name_b)
        trans_id_s = trans_id_b if isinstance(trans_id_b, str) else trans_id_b.decode()
        response.headers[TRANSACTION_ID] = trans_id_s

        # Check if file is completely uploaded and set meta
        if file_range.is_complete:
            Upload.meta_complete(item, '')
            item.meta[SIZE] = item.data.size
            item.close()
            background_compute_hash(current_app.storage, name)
            # Set status 'successful' and return the new URL for the uploaded file
            response.status = '201'
            response.headers["Content-Location"] = url_for('bepasty_apis.items_detail', name=name)
        else:
            item.close()
            response.status = '200'

        return response

    @rest_errorhandler
    def get(self):
        """
        Return the list of all files in bepasty, including metadata in the form:

            {
                "<name>": {
                    "file-meta": { <name.metadata> },
                    "uri" : "/apis/rest/items/<name>"
                },
                ...
            }
        """
        if not may(LIST):
            return 'Missing Permissions', 403
        ret = {}
        for meta in file_infos():
            name = meta.pop(ID)
            ret[name] = {'uri': url_for('bepasty_apis.items_detail', name=name),
                         'file-meta': meta}
        return jsonify(ret)


class ItemDetailView(DownloadView, RestBase):
    def err_incomplete(self, item, error):
        raise Conflict(description=error)

    def response(self, item, name):
        return jsonify({'uri': url_for('bepasty_apis.items_detail', name=name),
                        'file-meta': dict(item.meta)})

    @rest_errorhandler
    def get(self, name):
        return super(ItemDetailView, self).get(name)


class ItemDownloadView(ItemDetailView):
    def response(self, item, name):
        request_range = DownloadRange.from_request()
        if not request_range:
            size = item.data.size
            start = 0
        else:
            if request_range.end == -1:
                size = item.data.size
            else:
                size = min(request_range.end + 1, item.data.size)
            start = request_range.begin

        ret = Response(stream_with_context(self.stream(item, start, size)))
        ret.headers['Content-Disposition'] = '{0}; filename="{1}"'.format(
            self.content_disposition, item.meta[FILENAME])
        ret.headers['Content-Length'] = size - start
        ret.headers['Content-Type'] = item.meta[TYPE]  # 'application/octet-stream'
        ret.status = '200'
        ret.headers['Content-Range'] = ('bytes %d-%d/%d' % (start, size - 1, item.data.size))
        return ret

    @rest_errorhandler
    def get(self, name):
        return super(ItemDetailView, self).get(name)


class InfoView(RestBase):
    @rest_errorhandler
    def get(self):
        return jsonify({'MAX_BODY_SIZE': current_app.config['MAX_BODY_SIZE'],
                        'MAX_ALLOWED_FILE_SIZE': current_app.config['MAX_ALLOWED_FILE_SIZE']})
