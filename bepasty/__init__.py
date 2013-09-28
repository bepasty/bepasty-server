from flask import Flask
from .views import blueprint

def create_app():
    app = Flask(__name__)

    try:
        from flaskext.babel import Babel
        babel = Babel(app)
    except ImportError: pass

    app.config.from_object('bepasty.config.Config')
    app.config.from_envvar('BEPASTY_CONFIG')

    app.register_blueprint(blueprint)

    return app
