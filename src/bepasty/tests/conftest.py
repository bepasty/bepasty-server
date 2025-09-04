from os import close, unlink
from random import random
from tempfile import mkstemp

import pytest

from bepasty.app import create_app


@pytest.fixture(scope='module')
def app(request):
    """
    Create a bepasty app instance.
    """
    app = create_app()
    yield app
    unlink(app.config['DATABASE'])


@pytest.fixture(scope='module')
def testclient(request, app):
    """
    Create a Flask test client instance for bepasty.
    """
    db_file, app.config['DATABASE'] = mkstemp()
    # reset default permissions
    app.config['DEFAULT_PERMISSIONS'] = ''
    # set up a secret key
    app.config['SECRET_KEY'] = str(random())
    # set up permissions
    app.config['PERMISSIONS'] = {
        'l': 'list',
        'c': 'create',
        'r': 'read',
        'd': 'delete',
        'a': 'admin'
    }
    yield app.test_client()
    close(db_file)
