from flask import Blueprint

from .lodgeit import LodgeitUpload
from .rest import ItemDetailView, ItemDownloadView, ItemModifyView, \
    ItemUploadView, InfoView, ItemDeleteView, ItemLockView, ItemUnlockView


blueprint = Blueprint('bepasty_apis', __name__, url_prefix='/apis')

blueprint.add_url_rule('/lodgeit/', view_func=LodgeitUpload.as_view('lodgeit'))
blueprint.add_url_rule('/rest', view_func=InfoView.as_view('api_info'))
blueprint.add_url_rule('/rest/items', view_func=ItemUploadView.as_view('items'))
blueprint.add_url_rule('/rest/items/<itemname:name>', view_func=ItemDetailView.as_view('items_detail'))
blueprint.add_url_rule('/rest/items/<itemname:name>/download', view_func=ItemDownloadView.as_view('items_download'))
blueprint.add_url_rule('/rest/items/<itemname:name>/delete', view_func=ItemDeleteView.as_view('items_delete'))
blueprint.add_url_rule('/rest/items/<itemname:name>/modify', view_func=ItemModifyView.as_view('items_modify'))
blueprint.add_url_rule('/rest/items/<itemname:name>/lock', view_func=ItemLockView.as_view('items_lock'))
blueprint.add_url_rule('/rest/items/<itemname:name>/unlock', view_func=ItemUnlockView.as_view('items_unlock'))
