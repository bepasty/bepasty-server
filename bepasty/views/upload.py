from flask.views import MethodView

from . import blueprint


class UploadView(MethodView):
    def get(self):
        raise NotImplementedError

    def post(self):
        raise NotImplementedError


blueprint.add_url_rule('/+upload', view_func=UploadView.as_view('upload'))
