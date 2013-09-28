from flask.views import MethodView

from . import blueprint


class DisplayView(MethodView):
    def get(self):
        raise NotImplementedError


blueprint.add_url_rule('/<name>', view_func=DisplayView.as_view('display'))
