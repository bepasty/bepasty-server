import errno

from flask import current_app, render_template
from flask.views import MethodView
from werkzeug.exceptions import NotFound, Forbidden

from .. import constants
from ..utils import permissions
from ..utils.http import redirect_next_referrer


class DeleteView(MethodView):
    def post(self, name):
        if not permissions.may(permissions.DELETE):
            raise Forbidden()
        try:
            with current_app.storage.open(name) as item:
                if not item.meta[constants.COMPLETE] and not permissions.may(permissions.ADMIN):
                    error = 'Upload incomplete. Try again later.'
                    return render_template('error.html', heading=item.meta[constants.FILENAME], body=error), 409

                if item.meta[constants.LOCKED] and not permissions.may(permissions.ADMIN):
                    raise Forbidden()

            current_app.storage.remove(name)

        except (OSError, IOError) as e:
            if e.errno == errno.ENOENT:
                raise NotFound()
            raise

        return redirect_next_referrer('bepasty.index')
