# Copyright: 2014 Thomas Waldmann <tw@waldmann-edv.de>
# License: BSD 2-clause, see LICENSE for details.

import errno

from flask import current_app, redirect, url_for, render_template, abort
from flask.views import MethodView
from werkzeug.exceptions import NotFound

from . import blueprint
from ..utils.permissions import *


class LockView(MethodView):
    def get(self, name):
        if not may(ADMIN):
            abort(403)
        try:
            with current_app.storage.openwrite(name) as item:
                if item.meta.get('locked'):
                    error = 'File already locked.'
                elif not item.meta.get('complete'):
                    error = 'Upload incomplete. Try again later.'
                else:
                    error = None
                if error:
                    return render_template('display_error.html', name=name, item=item, error=error), 409
                item.meta['locked'] = True
            return redirect(url_for('bepasty.display', name=name))

        except (OSError, IOError) as e:
            if e.errno == errno.ENOENT:
                return render_template('file_not_found.html'), 404
            raise


class UnlockView(MethodView):
    def get(self, name):
        if not may(ADMIN):
            abort(403)
        try:
            with current_app.storage.openwrite(name) as item:
                if not item.meta.get('locked'):
                    error = 'File already unlocked.'
                elif not item.meta.get('complete'):
                    error = 'Upload incomplete. Try again later.'
                else:
                    error = None
                if error:
                    return render_template('display_error.html', name=name, item=item, error=error), 409
                item.meta['locked'] = False
            return redirect(url_for('bepasty.display', name=name))

        except (OSError, IOError) as e:
            if e.errno == errno.ENOENT:
                return render_template('file_not_found.html'), 404
            raise


blueprint.add_url_rule('/<itemname:name>/+lock', view_func=LockView.as_view('lock'))
blueprint.add_url_rule('/<itemname:name>/+unlock', view_func=UnlockView.as_view('unlock'))
