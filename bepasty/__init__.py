# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

from flask import Flask

from .storage import create_storage
from .views import blueprint
from .utils.name import setup_werkzeug_routing


def create_app():
    app = Flask(__name__)

    app.config.from_object('bepasty.config.Config')
    app.config.from_envvar('BEPASTY_CONFIG')

    create_storage(app)
    setup_werkzeug_routing(app)

    app.register_blueprint(blueprint)

    return app
