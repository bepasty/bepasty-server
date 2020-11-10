from flask import Blueprint

from .delete import DeleteView
from .display import DisplayView
from .download import DownloadView, InlineView
from .modify import ModifyView
from .qr import QRView
from .filelist import FileListView
from .index import index
from .login import LoginView, LogoutView
from .setkv import LockView, UnlockView
from .upload import UploadAbortView, UploadContinueView, UploadNewView, UploadView
from .xstatic import xstatic


blueprint = Blueprint('bepasty', __name__)

blueprint.add_url_rule('/', view_func=index)
blueprint.add_url_rule('/xstatic/<name>', defaults=dict(filename=''), view_func=xstatic)
blueprint.add_url_rule('/xstatic/<name>/<path:filename>', view_func=xstatic)
blueprint.add_url_rule('/+list', view_func=FileListView.as_view('filelist'))
blueprint.add_url_rule('/+login', view_func=LoginView.as_view('login'))
blueprint.add_url_rule('/+logout', view_func=LogoutView.as_view('logout'))
blueprint.add_url_rule('/<itemname:name>', view_func=DisplayView.as_view('display'))
blueprint.add_url_rule('/<itemname:name>/+delete', view_func=DeleteView.as_view('delete'))
blueprint.add_url_rule('/<itemname:name>/+download', view_func=DownloadView.as_view('download'))
blueprint.add_url_rule('/<itemname:name>/+inline', view_func=InlineView.as_view('inline'))
blueprint.add_url_rule('/<itemname:name>/+modify', view_func=ModifyView.as_view('modify'))
blueprint.add_url_rule('/<itemname:name>/+qr', view_func=QRView.as_view('qr'))
blueprint.add_url_rule('/<itemname:name>/+lock', view_func=LockView.as_view('lock'))
blueprint.add_url_rule('/<itemname:name>/+unlock', view_func=UnlockView.as_view('unlock'))
blueprint.add_url_rule('/+upload', view_func=UploadView.as_view('upload'))
blueprint.add_url_rule('/+upload/new', view_func=UploadNewView.as_view('upload_new'))
blueprint.add_url_rule('/+upload/<itemname:name>', view_func=UploadContinueView.as_view('upload_continue'))
blueprint.add_url_rule('/+upload/<itemname:name>/abort', view_func=UploadAbortView.as_view('upload_abort'))
