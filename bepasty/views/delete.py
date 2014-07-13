# Copyright: 2014 Dennis Schmalacker <github@progde.de>
# License: BSD 2-clause, see LICENSE for details.

import errno

from flask import current_app, render_template
from flask.views import MethodView
from werkzeug.exceptions import NotFound, Forbidden

from . import blueprint
from ..utils.permissions import *
from ..utils.http import redirect_next_referrer


class DeleteView(MethodView):
    def post(self, name):
        if not may(DELETE):
            raise Forbidden()
        try:
            with current_app.storage.open(name) as item:
                if not item.meta['complete'] and not may(ADMIN):
                    error = 'Upload incomplete. Try again later.'
                    return render_template('error.html', heading=item.meta['filename'], body=error), 409

                if item.meta['locked'] and not may(ADMIN):
                    raise Forbidden()

            current_app.storage.remove(name)

        except (OSError, IOError) as e:
            if e.errno == errno.ENOENT:
                raise NotFound()
            raise

        return redirect_next_referrer('bepasty.index')


blueprint.add_url_rule('/<itemname:name>/+delete', view_func=DeleteView.as_view('delete'))
