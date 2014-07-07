# License: BSD 2-clause, see LICENSE for details.

from flask import request, session
from flask.views import MethodView

from . import blueprint
from ..utils.permissions import *
from ..utils.http import redirect_next_referrer


class LoginView(MethodView):
    def post(self):
        token = request.form.get('token')
        if token is not None:
            permissions = lookup_permissions(token)
            if permissions is not None:
                session[PERMISSIONS] = permissions
                session[LOGGEDIN] = True
        return redirect_next_referrer('bepasty.index')


class LogoutView(MethodView):
    def post(self):
        # note: remove all session entries that are not needed for logged-out
        # state (because the code has defaults for them if they are missing).
        # if the session is empty. flask will automatically remove the cookie.
        session.pop(LOGGEDIN, None)
        session.pop(PERMISSIONS, None)
        return redirect_next_referrer('bepasty.index')


blueprint.add_url_rule('/+login', view_func=LoginView.as_view('login'))
blueprint.add_url_rule('/+logout', view_func=LogoutView.as_view('logout'))
