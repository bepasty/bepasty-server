import errno

from flask import current_app, render_template
from flask.views import MethodView
from werkzeug.exceptions import NotFound, Forbidden

from ..constants import COMPLETE, FILENAME, LOCKED
from ..utils.http import redirect_next_referrer
from ..utils.permissions import ADMIN, DELETE, may


class DeleteView(MethodView):
    def post(self, name):
        if not may(DELETE):
            raise Forbidden()
        try:
            with current_app.storage.open(name) as item:
                if not item.meta[COMPLETE] and not may(ADMIN):
                    error = 'Upload incomplete. Try again later.'
                    return render_template('error.html', heading=item.meta[FILENAME], body=error), 409

                if item.meta[LOCKED] and not may(ADMIN):
                    raise Forbidden()

            current_app.storage.remove(name)

        except (OSError, IOError) as e:
            if e.errno == errno.ENOENT:
                raise NotFound()
            raise

        return redirect_next_referrer('bepasty.index')
