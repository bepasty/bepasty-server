import errno

from flask import current_app, request, render_template
from flask.views import MethodView
from werkzeug.exceptions import Forbidden, NotFound

from ..constants import COMPLETE, FILENAME, LOCKED, TYPE
from ..utils.date_funcs import delete_if_lifetime_over
from ..utils.http import redirect_next_referrer
from ..utils.permissions import ADMIN, CREATE, may
from ..utils.upload import Upload


class ModifyView(MethodView):
    def error(self, item, error):
        return render_template('error.html', heading=item.meta[FILENAME], body=error), 409

    def response(self, name):
        return redirect_next_referrer('bepasty.display', name=name)

    def get_params(self):
        return {
            FILENAME: request.form.get('filename'),
            TYPE: request.form.get('contenttype'),
        }

    def post(self, name):
        if not may(CREATE):
            raise Forbidden()

        try:
            with current_app.storage.openwrite(name) as item:
                if not item.meta[COMPLETE] and not may(ADMIN):
                    error = 'Upload incomplete. Try again later.'
                    return self.error(item, error)

                if item.meta[LOCKED] and not may(ADMIN):
                    raise Forbidden()

                if delete_if_lifetime_over(item, name):
                    raise NotFound()

                params = self.get_params()
                if params[FILENAME]:
                    item.meta[FILENAME] = Upload.filter_filename(
                        params[FILENAME], name, params[TYPE], item.meta[TYPE]
                    )
                if params[TYPE]:
                    item.meta[TYPE], _ = Upload.filter_type(
                        params[TYPE], item.meta[TYPE]
                    )

                return self.response(name)

        except (OSError, IOError) as e:
            if e.errno == errno.ENOENT:
                raise NotFound()
            raise
