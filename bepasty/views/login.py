# License: BSD 2-clause, see LICENSE for details.

from flask import current_app, redirect, request, url_for, session
from flask.views import MethodView

from . import blueprint


class LoginView(MethodView):
    def post(self):
        token = request.form.get('token')
        if token is not None and token in current_app.config['TOKENS']:
            session['may_upload'] = True
        return redirect(url_for('bepasty.index'))


class LogoutView(MethodView):
    def post(self):
        session['may_upload'] = False
        return redirect(url_for('bepasty.index'))


blueprint.add_url_rule('/+login', view_func=LoginView.as_view('login'))
blueprint.add_url_rule('/+logout', view_func=LogoutView.as_view('logout'))
