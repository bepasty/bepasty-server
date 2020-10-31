import os
import time
import re

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
    LIST,
    READ,
    get_permission_icons,
    get_permissions,
    logged_in,
    may,
)
from .views import blueprint


class PrefixMiddleware(object):
    def __init__(self, app, prefix=''):
        self.app = app
        self.prefix = prefix

    def __call__(self, environ, start_response, set_script_name=True):
        if environ['PATH_INFO'].startswith(self.prefix):
            environ['PATH_INFO'] = environ['PATH_INFO'][len(self.prefix):]
            if set_script_name:
                environ['SCRIPT_NAME'] = self.prefix
            return self.app(environ, start_response)
        else:
            start_response('404', [('Content-Type', 'text/plain')])
            return ['This URL does not belong to the bepasty app.'.encode()]


class ReverseProxyMiddleware(PrefixMiddleware):
    def __init__(self, app, scheme, server, script_name='', prefix=None):
        self.app = app
        self.scheme = scheme
        self.server = server
        self.script_name = script_name or ''
        self.prefix = prefix
        if prefix is not None:
            super(ReverseProxyMiddleware, self).__init__(app, prefix=prefix)

    def __call__(self, environ, start_response):
        scheme = environ.get('HTTP_X_FORWARDED_PROTO') or self.scheme
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        host = environ.get('HTTP_X_FORWARDED_HOST') or self.server
        if host:
            environ['HTTP_HOST'] = host
        script_name = environ.get('HTTP_X_FORWARDED_PREFIX') or self.script_name
        environ['SCRIPT_NAME'] = script_name

        if self.prefix is not None:
            return super(ReverseProxyMiddleware, self).__call__(
                environ, start_response, set_script_name=False
            )
        else:
            return self.app(environ, start_response)


def create_app():
    app = Flask(__name__)

    app.config.from_object('bepasty.config.Config')
    if os.environ.get('BEPASTY_CONFIG'):
        app.config.from_envvar('BEPASTY_CONFIG')

    public_url = app.config.get('PUBLIC_URL')
    prefix = app.config.get('APP_BASE_PATH')
    if public_url is not None:
        m = re.match('(https?)://([^/]+)(/.*)?', public_url.rstrip('/'))
        if m:
            app.wsgi_app = ReverseProxyMiddleware(app.wsgi_app,
                                                  scheme=m.group(1),
                                                  server=m.group(2),
                                                  script_name=m.group(3),
                                                  prefix=prefix)
        else:
            raise Exception("could not parse PUBLIC_URL [%s]" % public_url)
    elif prefix is not None:
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
    app.jinja_env.globals['READ'] = READ
    app.jinja_env.globals['DELETE'] = DELETE

    return app
