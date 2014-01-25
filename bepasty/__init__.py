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
    if os.environ.get('BEPASTY_CONFIG'):
        app.config.from_envvar('BEPASTY_CONFIG')

    create_storage(app)
    setup_werkzeug_routing(app)

    app.register_blueprint(blueprint)

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('_error_404.html'), 404

    return app


def server_cli():
    """Create command-line interface for bepasty server"""

    import argparse

    parser = argparse.ArgumentParser(
        description="The free and open-source paste bin and trash can "
                    "for your stuff.")
    parser.add_argument('--host', help='Host to listen on')
    parser.add_argument('--port', type=int, help='Port to listen on')
    parser.add_argument('--debug', help='Activate debug mode',
                        action='store_true')
    args = parser.parse_args()

    app = create_app()

    print " * Starting bepasty server..."
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug
    )
