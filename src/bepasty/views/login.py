from flask import request, session
from flask.views import MethodView

from ..utils import permissions
from ..utils.http import redirect_next_referrer


class LoginView(MethodView):
    def post(self):
        token = request.form.get('token')
        if token is not None:
            permissions_for_token = permissions.lookup_permissions(token)
            if permissions_for_token is not None:
                session[permissions.PERMISSIONS] = permissions_for_token
                session[permissions.LOGGEDIN] = True
        return redirect_next_referrer('bepasty.index')


class LogoutView(MethodView):
    def post(self):
        # note: remove all session entries that are not needed for logged-out
        # state (because the code has defaults for them if they are missing).
        # if the session is empty. flask will automatically remove the cookie.
        session.pop(permissions.LOGGEDIN, None)
        session.pop(permissions.PERMISSIONS, None)
        return redirect_next_referrer('bepasty.index')
