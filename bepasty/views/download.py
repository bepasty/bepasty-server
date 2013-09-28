from flask.views import MethodView

from . import blueprint


class DownloadView(MethodView):
    def get(self):
        raise NotImplementedError


blueprint.add_url_rule('/<name>/+download', view_func=DownloadView.as_view('download'))
