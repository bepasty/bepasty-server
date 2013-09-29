# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

import errno

from flask import current_app, render_template, request
from flask.views import MethodView
from werkzeug.exceptions import NotFound

from ..utils.name import ItemName
from . import blueprint


class DisplayView(MethodView):
    def get(self, name):
        try:
            item = current_app.storage.open(name)
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise NotFound()
            raise

        with item as item:
            if not item.meta['complete']:
                error = 'Upload incomplete. Try again later.'
                return render_template('display_error.html', name=name, item=item, error=error), 409
            return render_template('display.html', name=name, item=item)


blueprint.add_url_rule('/<itemname:name>', view_func=DisplayView.as_view('display'))
