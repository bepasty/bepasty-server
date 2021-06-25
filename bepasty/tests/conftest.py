from os import close, unlink
from random import random
from tempfile import mkstemp

import pytest

from bepasty.app import create_app


@pytest.yield_fixture(scope='module')
def app(request):
    """
    creates a bepasty App-Instance
    """
    app = create_app()
    yield app
    unlink(app.config['DATABASE'])


@pytest.yield_fixture(scope='module')
def testclient(request, app):
    """
    creates a Flask-testclient instance for bepasty
    """
    db_file, app.config['DATABASE'] = mkstemp()
    # reset default permissions
    app.config['DEFAULT_PERMISSIONS'] = ''
    # setup a secret key
    app.config['SECRET_KEY'] = str(random())
    # setup permissions
    app.config['PERMISSIONS'] = {
        'l': 'list',
        'c': 'create',
        'r': 'read',
        'd': 'delete',
        'a': 'admin'
    }
    yield app.test_client()
    close(db_file)
