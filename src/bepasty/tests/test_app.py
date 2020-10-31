#
# app tests
#

from flask import request, url_for
from flask.views import MethodView

import pytest

from ..app import create_app
from ..config import Config


@pytest.fixture
def app_fixture():
    app_base_path = Config.APP_BASE_PATH
    public_url = Config.PUBLIC_URL

    yield

    Config.APP_BASE_PATH = app_base_path
    Config.PUBLIC_URL = public_url


class TestView(MethodView):
    callback = None

    def get(self):
        TestView.callback()
        return 'done'


def prepare(callback):
    app = create_app()
    app.add_url_rule('/test_call', view_func=TestView.as_view('test.test_call'))

    TestView.callback = staticmethod(callback)
    client = app.test_client()

    assert app.config['APP_BASE_PATH'] == Config.APP_BASE_PATH
    assert app.config['PUBLIC_URL'] == Config.PUBLIC_URL

    return app, client


def test_none(app_fixture):
    Config.APP_BASE_PATH = None
    Config.PUBLIC_URL = None

    def none_callback():
        url = url_for('test.test_call')
        assert url == request.path
        url = url_for('test.test_call', _external=True)
        assert url == 'http://localhost' + request.path

    app, client = prepare(none_callback)

    response = client.get('/bepasty/test_call')
    assert response.status_code == 404

    response = client.get('/test_call')
    assert response.status_code == 200
    assert response.data == 'done'.encode()


def test_prefix(app_fixture):
    Config.APP_BASE_PATH = '/bepasty'
    Config.PUBLIC_URL = None

    def prefix_callback():
        url = url_for('test.test_call')
        assert url == Config.APP_BASE_PATH + request.path
        url = url_for('test.test_call', _external=True)
        assert url == 'http://localhost' + Config.APP_BASE_PATH + request.path

    app, client = prepare(prefix_callback)

    response = client.get('/test_call')
    assert response.status_code == 404

    response = client.get('/bepasty/test_call')
    assert response.status_code == 200
    assert response.data == 'done'.encode()


def test_proxy(app_fixture):
    Config.APP_BASE_PATH = None
    public_base = '/bepasty1'
    Config.PUBLIC_URL = 'https://example.org' + public_base

    def proxy_callback():
        url = url_for('test.test_call')
        assert url == public_base + request.path
        url = url_for('test.test_call', _external=True)
        assert url == Config.PUBLIC_URL + request.path

    app, client = prepare(proxy_callback)

    response = client.get('/bepasty2/test_call')
    assert response.status_code == 404
    response = client.get('/bepasty1/test_call')
    assert response.status_code == 404

    response = client.get('/test_call')
    assert response.status_code == 200
    assert response.data == 'done'.encode()


def test_proxy_env(app_fixture):
    Config.APP_BASE_PATH = None
    public_base = '/bepasty1'
    Config.PUBLIC_URL = 'https://example.org' + public_base
    env_public_proto = 'https'
    env_public_host = 'example2.org'
    env_public_port = '5000'
    env_public_base = '/bepasty3'
    env_public_url = '{}://{}:{}{}'.format(env_public_proto, env_public_host,
                                           env_public_port, env_public_base)

    def proxy_callback():
        url = url_for('test.test_call')
        assert url == env_public_base + request.path
        url = url_for('test.test_call', _external=True)
        assert url == env_public_url + request.path

    app, client = prepare(proxy_callback)

    # public url is overwritten by proxy environ
    client.environ_base['HTTP_X_FORWARDED_PROTO'] = env_public_proto
    client.environ_base['HTTP_X_FORWARDED_HOST'] = env_public_host
    client.environ_base['HTTP_X_FORWARDED_PORT'] = env_public_port
    client.environ_base['HTTP_X_FORWARDED_PREFIX'] = env_public_base

    response = client.get('/bepasty2/test_call')
    assert response.status_code == 404
    response = client.get('/bepasty1/test_call')
    assert response.status_code == 404

    response = client.get('/test_call')
    assert response.status_code == 200
    assert response.data == 'done'.encode()


def test_proxy_prefix(app_fixture):
    Config.APP_BASE_PATH = '/bepasty2'
    public_base = '/bepasty1'
    Config.PUBLIC_URL = 'https://example.org' + public_base

    def proxy_prefix_callback():
        url = url_for('test.test_call')
        assert url == public_base + request.path
        url = url_for('test.test_call', _external=True)
        assert url == Config.PUBLIC_URL + request.path

    app, client = prepare(proxy_prefix_callback)

    response = client.get('/test_call')
    assert response.status_code == 404
    response = client.get('/bepasty1/test_call')
    assert response.status_code == 404

    response = client.get('/bepasty2/test_call')
    assert response.status_code == 200
    assert response.data == 'done'.encode()


def test_proxy_prefix_slash(app_fixture):
    Config.APP_BASE_PATH = '/bepasty2'
    public_base = '/bepasty1'
    public_url = 'https://example.org' + public_base
    Config.PUBLIC_URL = public_url + '/'

    def proxy_prefix_callback():
        url = url_for('test.test_call')
        assert url == public_base + request.path
        url = url_for('test.test_call', _external=True)
        assert url == public_url + request.path

    app, client = prepare(proxy_prefix_callback)

    response = client.get('/test_call')
    assert response.status_code == 404
    response = client.get('/bepasty1/test_call')
    assert response.status_code == 404

    response = client.get('/bepasty2/test_call')
    assert response.status_code == 200
    assert response.data == 'done'.encode()
