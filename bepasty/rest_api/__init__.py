# Copyright: 2014 Dennis Schmalacker <github@progde.de>
# License: BSD 2-clause, see LICENSE for details.

from flask import Blueprint, current_app, jsonify
from flask.views import MethodView

rest_api = Blueprint('bepasty_rest', __name__, url_prefix='/api/v1')

from . import (
    items)

class InfoView(MethodView):
    def get(self):
        return jsonify({'EXPECTED_CHUNK_SIZE':current_app.config['EXPECTED_CHUNK_SIZE']})


rest_api.add_url_rule('/', view_func=InfoView.as_view('api_info'))
