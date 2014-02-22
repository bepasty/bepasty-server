import hashlib

from . import rest_api
from flask.views import MethodView
from flask import request, make_response, current_app, url_for, jsonify

from ..utils.name import ItemName

class Upload(object):
	@staticmethod
	def data(item, stream, size_input, offset=0):
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

	        buf = stream.read(read_length)
	        if not buf:
	            # Should not happen, we already checked the size
	            raise RuntimeError

	        item.data.write(buf, offset + size_written)
	        hasher.update(buf)

	        len_buf = len(buf)
	        size_written += len_buf
	        size_input -= len_buf

	    return size_written, hasher.hexdigest()

class ItemsView(MethodView):
	def post(self):
		name = ItemName.create()
		if request.headers.get('Content-Type') == 'application/octet-stream':
			with current_app.storage.create(name, int(request.headers.get("Content-Length"))) as item:
				item.meta['type'] = 'application/octet-stream'
				item.meta['unlocked'] = current_app.config['UPLOAD_UNLOCKED']
				item.meta['size'], item.meta['hash'] = Upload.data(item, request.stream, int(request.headers.get("Content-Length")))
				item.meta['complete'] = True
		else:
			return 'Content-Type is not application/octet-stream', 400
		return jsonify({'uri': url_for('bepasty_rest.items_detail', name=name),
						'size': item.meta['size'],
						'sha256hash' : item.meta['hash']})


class ItemDetailView(MethodView):
	def get(self):
		return 'Hello World'

rest_api.add_url_rule('/items', view_func=ItemsView.as_view('items'))
rest_api.add_url_rule('/items/<itemname:name>', view_func=ItemDetailView.as_view('items_detail'))
#rest_api.add_url_rule('/items/<itemname:name>/data', view_func=ItemsDataView.as_view('items_data'))
#rest_api.add_url_rule('/items/<itemname:name>/meta', view_func=ItemsMetaView.as_view('items_meta'))
