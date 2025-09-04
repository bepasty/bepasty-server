from flask import request, session
from flask.views import MethodView

from ..utils.http import redirect_next_referrer
from ..utils.permissions import LOGGEDIN, PERMISSIONS, lookup_permissions


class LoginView(MethodView):
    def post(self):
        token = request.form.get('token')
        if token is not None:
            permissions_for_token = lookup_permissions(token)
            if permissions_for_token is not None:
                session[PERMISSIONS] = permissions_for_token
                session[LOGGEDIN] = True
        return redirect_next_referrer('bepasty.index')


class LogoutView(MethodView):
    def post(self):
        # Note: Remove all session entries that are not needed for the logged-out
        # state (because the code has defaults for them if they are missing).
        # If the session is empty, Flask will automatically remove the cookie.
        session.pop(LOGGEDIN, None)
        session.pop(PERMISSIONS, None)
        return redirect_next_referrer('bepasty.index')
