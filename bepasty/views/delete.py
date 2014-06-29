# Copyright: 2014 Dennis Schmalacker <github@progde.de>
# License: BSD 2-clause, see LICENSE for details.

import errno

from flask import current_app, redirect, url_for, render_template, abort
from flask.views import MethodView
from werkzeug.exceptions import NotFound

from . import blueprint
from ..utils.permissions import *


class DeleteView(MethodView):
    def get(self, name):
        if not may(DELETE):
            abort(403)
        try:
            item = current_app.storage.open(name)
        except (OSError, IOError) as e:
            if e.errno == errno.ENOENT:
                return render_template('file_not_found.html'), 404
            raise

        if item.meta.get('locked'):
            error = 'File locked.'
        elif not item.meta.get('complete'):
            error = 'Upload incomplete. Try again later.'
        else:
            error = None
        if error:
            try:
                return render_template('display_error.html', name=name, item=item, error=error), 409
            finally:
                item.close()

        try:
            item = current_app.storage.remove(name)
        except (OSError, IOError) as e:
            if e.errno == errno.ENOENT:
                return render_template('file_not_found.html'), 404

        return redirect(url_for('bepasty.display', name=name))

blueprint.add_url_rule('/<itemname:name>/+delete', view_func=DeleteView.as_view('delete'))
