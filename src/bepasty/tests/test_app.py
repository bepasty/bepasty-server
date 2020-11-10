#
# app tests
#

from flask import request, url_for
from flask.views import MethodView

from ..app import create_app
from ..config import Config


def test_secret_key(monkeypatch):
    monkeypatch.setattr(Config, 'PERMISSIONS', {
        'admin': 'admin,list,create,read,delete',
        'full': 'list,create,read,delete',
        'none': '',
    })
    monkeypatch.setattr(Config, 'SECRET_KEY', 'secret')

    app = create_app()
    secret_key = app.config['SECRET_KEY']
    assert len(secret_key) > len(Config.SECRET_KEY)

    Config.PERMISSIONS = {
        'admin': 'admin,list,create,read,delete',
        'none': '',
    }
    app = create_app()
    assert app.config['SECRET_KEY'] != secret_key


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

    return app, client


def test_none(monkeypatch):
    monkeypatch.setattr(Config, 'APP_BASE_PATH', None)

    def none_callback():
        url = url_for('test.test_call')
        assert url == request.path

    app, client = prepare(none_callback)

    response = client.get('/bepasty/test_call')
    assert response.status_code == 404

    response = client.get('/test_call')
    assert response.status_code == 200
    assert response.data == b'done'


def test_prefix(monkeypatch):
    monkeypatch.setattr(Config, 'APP_BASE_PATH', '/bepasty')

    def prefix_callback():
        url = url_for('test.test_call')
        assert url == Config.APP_BASE_PATH + request.path

    app, client = prepare(prefix_callback)

    response = client.get('/test_call')
    assert response.status_code == 404

    response = client.get('/bepasty/test_call')
    assert response.status_code == 200
    assert response.data == b'done'
