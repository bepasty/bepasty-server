import os
import time
import hashlib

from flask import (
    Flask,
    Markup,
    current_app,
    g as flaskg,  # searching for 1 letter name "g" isn't nice, thus we use flaskg
    render_template,
    session,
)

from .apis import blueprint as blueprint_apis
from .storage import create_storage
from .utils.name import setup_werkzeug_routing
from .utils.permissions import (
    ADMIN,
    CREATE,
    DELETE,
    MODIFY,
    LIST,
    READ,
    get_permission_icons,
    get_permissions,
    logged_in,
    may,
)
from .views import blueprint

import mimetypes
mimetypes.add_type('application/x-asciinema-recording', '.cast')


class PrefixMiddleware(object):
    def __init__(self, app, prefix=''):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response):
        if environ['PATH_INFO'].startswith(self.prefix):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
            environ['SCRIPT_NAME'] = self.prefix
            return self.app(environ, start_response)
        else:
            start_response('404', [('Content-Type', 'text/plain')])
            return ['This URL does not belong to the bepasty app.'.encode()]


def setup_secret_key(app):
    """
    The secret key is used to sign cookies and cookies not signed with the
    current secret key are considered invalid.

    Here, we amend the configured secret key, so it depends on some
    other config values. Changing any of these values will change the
    computed secret key (and thus invalidate all previously made
    cookies).

    Currently supported secret-changing config values: PERMISSIONS
    """
    # if app.config['SECRET_KEY'] is empty, keep as NullSession
    if app.config['SECRET_KEY']:
        perms = sorted(k + v for k, v in app.config['PERMISSIONS'].items())
        perms = ''.join(perms).encode()
        app.config['SECRET_KEY'] += hashlib.sha256(perms).hexdigest()


def create_app():
    app = Flask(__name__)

    app.config.from_object('bepasty.config.Config')
    if os.environ.get('BEPASTY_CONFIG'):
        app.config.from_envvar('BEPASTY_CONFIG')

    setup_secret_key(app)

    prefix = app.config.get('APP_BASE_PATH')
    if prefix is not None:
        app.wsgi_app = PrefixMiddleware(app.wsgi_app, prefix=prefix)

    app.storage = create_storage(app)
    setup_werkzeug_routing(app)

    app.register_blueprint(blueprint)
    app.register_blueprint(blueprint_apis)

    @app.errorhandler(403)
    def url_forbidden(e):
        heading = 'Forbidden'
        body = Markup("""\
            <p>
                You are not allowed to access the requested URL.
            </p>
            <p>
                If you entered the URL manually please check your spelling and try again.
            </p>
            <p>
                Also check if you maybe forgot to log in or if your permissions are insufficient for this.
            </p>
""")
        return render_template('error.html', heading=heading, body=body), 403

    @app.errorhandler(404)
    def url_not_found(e):
        heading = 'Not found'
        body = Markup("""\
            <p>
                The requested URL was not found on the server.
            </p>
            <p>
                If you entered the URL manually please check your spelling and try again.
            </p>
""")
        return render_template('error.html', heading=heading, body=body), 404

    @app.before_request
    def before_request():
        """
        before the request is handled (by its view function), we compute some
        stuff here and make it easily available.
        """
        flaskg.logged_in = logged_in()
        flaskg.permissions = get_permissions()
        flaskg.icon_permissions = get_permission_icons()
        if flaskg.logged_in:
            session.permanent = current_app.config['PERMANENT_SESSION']

    def datetime_format(ts):
        """
        takes a unix timestamp and outputs a iso8601-like formatted string.
        times are always UTC, but we don't include the TZ here for brevity.
        it should be made clear (e.g. in the template) that the date/time is UTC.
        """
        if not ts:  # we use 0 to indicate undefined time
            return 'undefined'
        return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(ts))

    app.jinja_env.filters['datetime'] = datetime_format

    app.jinja_env.globals['flaskg'] = flaskg
    app.jinja_env.globals['may'] = may
    app.jinja_env.globals['ADMIN'] = ADMIN
    app.jinja_env.globals['LIST'] = LIST
    app.jinja_env.globals['CREATE'] = CREATE
    app.jinja_env.globals['MODIFY'] = MODIFY
    app.jinja_env.globals['READ'] = READ
    app.jinja_env.globals['DELETE'] = DELETE

    return app
