"""
Set metadata keys to specific values
"""

import errno

from flask import current_app, render_template
from flask.views import MethodView
from werkzeug.exceptions import NotFound, Forbidden

from .. import constants
from ..utils import permissions
from ..utils.http import redirect_next_referrer


class SetKeyValueView(MethodView):
    # overwrite these in subclasses:
    REQUIRED_PERMISSION = None
    KEY = None
    NEXT_VALUE = None

    def post(self, name):
        if self.REQUIRED_PERMISSION is not None and not permissions.may(self.REQUIRED_PERMISSION):
            raise Forbidden()
        try:
            with current_app.storage.openwrite(name) as item:
                if item.meta[self.KEY] == self.NEXT_VALUE:
                    error = '%s already is %r.' % (self.KEY, self.NEXT_VALUE)
                elif not item.meta[constants.COMPLETE]:
                    error = 'Upload incomplete. Try again later.'
                else:
                    error = None
                if error:
                    return render_template('error.html', heading=item.meta[constants.FILENAME], body=error), 409
                item.meta[self.KEY] = self.NEXT_VALUE
            return redirect_next_referrer('bepasty.display', name=name)

        except (OSError, IOError) as e:
            if e.errno == errno.ENOENT:
                raise NotFound()
            raise


class LockView(SetKeyValueView):
    REQUIRED_PERMISSION = permissions.ADMIN
    KEY = constants.LOCKED
    NEXT_VALUE = True


class UnlockView(SetKeyValueView):
    REQUIRED_PERMISSION = permissions.ADMIN
    KEY = constants.LOCKED
    NEXT_VALUE = False
