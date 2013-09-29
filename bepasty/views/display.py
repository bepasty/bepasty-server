# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

from flask import current_app, render_template, request
from flask.views import MethodView

from ..utils.name import ItemName
from . import blueprint


class DisplayView(MethodView):
    def get(self, name):
        with current_app.storage.open(name) as item:
            return render_template('display.html', name=name, item=item)


blueprint.add_url_rule('/<itemname:name>', view_func=DisplayView.as_view('display'))
