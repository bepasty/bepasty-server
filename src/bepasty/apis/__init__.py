from flask import Blueprint

from .lodgeit import LodgeitUpload
from .rest import ItemDetailView, ItemDownloadView, ItemUploadView, InfoView


blueprint = Blueprint('bepasty_apis', __name__, url_prefix='/apis')

blueprint.add_url_rule('/lodgeit/', view_func=LodgeitUpload.as_view('lodgeit'))
blueprint.add_url_rule('/rest', view_func=InfoView.as_view('api_info'))
blueprint.add_url_rule('/rest/items', view_func=ItemUploadView.as_view('items'))
blueprint.add_url_rule('/rest/items/<itemname:name>', view_func=ItemDetailView.as_view('items_detail'))
blueprint.add_url_rule('/rest/items/<itemname:name>/download', view_func=ItemDownloadView.as_view('items_download'))
