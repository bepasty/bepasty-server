from flask import Flask

def create_app():
    app = Flask(__name__)

    try:
        from flaskext.babel import Babel
        babel = Babel(app)
    except ImportError: pass

    app.config.from_object('bepasty.config.Config')
    app.config.from_envvar('BEPASTY_CONFIG')

    return app
