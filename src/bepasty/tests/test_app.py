#
# app tests
#

from ..app import create_app
from ..config import Config


def test_secret_key():
    Config.PERMISSIONS = {
        'admin': 'admin,list,create,read,delete',
        'full': 'list,create,read,delete',
        'none': '',
    }
    Config.SECRET_KEY = 'secret'

    app = create_app()
    secret_key = app.config['SECRET_KEY']
    assert len(secret_key) > len(Config.SECRET_KEY)

    Config.PERMISSIONS = {
        'admin': 'admin,list,create,read,delete',
        'none': '',
    }
    app = create_app()
    assert app.config['SECRET_KEY'] != secret_key
