from flask import current_app, request
from flask.views import MethodView

from ..utils.name import ItemName
from . import blueprint


class DisplayView(MethodView):
    def get(self, name):
        n = ItemName.parse(name)
        raise NotImplementedError


blueprint.add_url_rule('/<name>', view_func=DisplayView.as_view('display'))
