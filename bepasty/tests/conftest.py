from os import close, unlink
from random import random
from tempfile import mkstemp

import pytest

from bepasty.app import create_app, create_storage


@pytest.fixture(scope='module')
def testclient(request):
    '''
    creates a Flask-testclient instance for bepasty
    '''
    app = create_app()
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

    def teardown():
        close(db_file)
        unlink(app.config['DATABASE'])
    request.addfinalizer(teardown)
    return app.test_client()
