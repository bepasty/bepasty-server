import errno
import base64
import time
from io import BytesIO

from flask import Response, make_response, url_for, jsonify, stream_with_context, request, current_app
from flask.views import MethodView

from ..constants import COMPLETE, FILENAME, SIZE, TYPE
from ..utils.date_funcs import get_maxlife
from ..utils.http import ContentRange, DownloadRange
from ..utils.name import ItemName
from ..utils.permissions import CREATE, LIST, READ, may
from ..utils.upload import Upload, background_compute_hash


class ItemUploadView(MethodView):
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
        * Transaction-Id: The Transaction-Id for Chunked Uploads.
            Needs to be delivered when uploading in chunks (after the first chunk).

        To start an upload, the HTTP Headers need to be delivered.
        The body of the request needs to be the base64 encoded file contents.
        Content-Length is the original file size before base64 encoding.
        Content-Range follows the same logic.
        After the first chunk is uploaded, bepasty will return the Transaction-Id to continue the upload.
        Deliver the Transaction-Id and the correct Content-Range to continue upload.
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
        if not request.headers.get("Transaction-Id"):
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
            name = base64.b64decode(request.headers.get("Transaction-Id"))
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
        response.headers["transaction-id"] = base64.b64encode(name)
        response.status = '200'

        # Check if file is completely uploaded and set meta
        if file_range.is_complete:
            Upload.meta_complete(item, '')
            item.meta[SIZE] = item.data.size
            item.close()

            background_compute_hash(current_app.storage, name)
            # Set status 'successful' and return the new URL for the uploaded file
            response.status = '201'
            response.headers["Content-Location"] = url_for('bepasty_apis.items_detail', name=name)
            response.headers["Transaction-ID"] = base64.b64encode(name)
        else:
            item.close()

        return response

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
        for name in current_app.storage:
            item = current_app.storage.open(name)
            ret[name] = {'uri': url_for('bepasty_apis.items_detail', name=name),
                         'file-meta': dict(item.meta)}
        return jsonify(ret)


class ItemDetailView(MethodView):
    def get(self, name):
        if not may(READ):
            return 'Missing Permissions', 403

        with current_app.storage.open(name) as item:
            return jsonify({'uri': url_for('bepasty_apis.items_detail', name=name),
                            'file-meta': dict(item.meta)})


class ItemDownloadView(MethodView):
    content_disposition = 'attachment'

    def get(self, name):
        if not may(READ):
            return 'Missing Permissions', 403

        try:
            item = current_app.storage.open(name)
        except (OSError, IOError) as e:
            if e.errno == errno.ENOENT:
                return 'File not found', 404
            raise

        if item.meta.get():
            error = 'File Locked.'
        elif not item.meta.get(COMPLETE):
            error = 'Upload incomplete. Try again later.'
        else:
            error = None
        if error:
            item.close()
            return error, 403

        request_range = DownloadRange.from_request()
        if not request_range:
            range_end = item.data.size - 1
            range_begin = 0
        else:
            if request_range.end == -1:
                range_end = item.data.size - 1
            else:
                range_end = min(request_range.end, item.data.size - 1)
            range_begin = request_range.begin

        def stream(begin, end):
            offset = max(0, begin)
            with item as _item:
                while offset <= end:
                    buf = _item.data.read(16 * 1024, offset)
                    offset += len(buf)
                    yield buf

        ret = Response(stream_with_context(stream(range_begin, range_end)))
        ret.headers['Content-Disposition'] = '{0}; filename="{1}"'.format(
            self.content_disposition, item.meta[FILENAME])
        ret.headers['Content-Length'] = (range_end - range_begin) + 1
        ret.headers['Content-Type'] = item.meta[TYPE]  # 'application/octet-stream'
        ret.status = '200'
        ret.headers['Content-Range'] = ('bytes %d-%d/%d' % (range_begin, range_end, item.data.size))
        return ret


class InfoView(MethodView):
    def get(self):
        return jsonify({'MAX_BODY_SIZE': current_app.config['MAX_BODY_SIZE'],
                        'MAX_ALLOWED_FILE_SIZE': current_app.config['MAX_ALLOWED_FILE_SIZE']})
