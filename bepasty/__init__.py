# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

import os

from flask import Flask, render_template

from .storage import create_storage
from .views import blueprint
from .utils.name import setup_werkzeug_routing


def create_app():
    app = Flask(__name__)

    app.config.from_object('bepasty.config.Config')
    if 'BEPASTY_CONFIG' in os.environ:
        app.config.from_envvar('BEPASTY_CONFIG')

    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

    create_storage(app)
    setup_werkzeug_routing(app)

    app.register_blueprint(blueprint)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('_error_404.html'), 404

    return app
