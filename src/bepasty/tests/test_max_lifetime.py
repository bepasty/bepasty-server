#
# Limiting the maximum lifetime of uploaded items (MAX_LIFETIME)
#

import time

import pytest

from ..app import create_app
from ..config import Config
from ..constants import FOREVER, TIMESTAMP_MAX_LIFE
from ..utils.date_funcs import allowed_maxlife_units, limit_maxlife

DAY = 24 * 3600
WEEK = 7 * DAY


def make_app(tmp_path, monkeypatch, max_lifetime):
    monkeypatch.setattr(Config, 'STORAGE_FILESYSTEM_DIRECTORY', str(tmp_path))
    monkeypatch.setattr(Config, 'SECRET_KEY', 'secret')
    monkeypatch.setattr(Config, 'DEFAULT_PERMISSIONS', 'create,read')
    monkeypatch.setattr(Config, 'MAX_LIFETIME', max_lifetime)
    monkeypatch.delenv('BEPASTY_CONFIG', raising=False)
    app = create_app()
    app.config['TESTING'] = True
    return app


@pytest.fixture
def app(tmp_path, monkeypatch):
    return make_app(tmp_path, monkeypatch, 2 * WEEK)


@pytest.fixture
def app_unlimited(tmp_path, monkeypatch):
    return make_app(tmp_path, monkeypatch, None)


@pytest.mark.parametrize('secs, expected', [
    (DAY, DAY),
    (2 * WEEK, 2 * WEEK),
    (3 * WEEK, 2 * WEEK),
    (FOREVER, 2 * WEEK),
    (0, 2 * WEEK),
    (-5, 2 * WEEK),
])
def test_limit_maxlife(app, secs, expected):
    with app.app_context():
        assert limit_maxlife(secs) == expected


@pytest.mark.parametrize('secs, expected', [
    (DAY, DAY),
    (FOREVER, FOREVER),
    (0, FOREVER),  # 0 and negative values never expired, so they are FOREVER
    (-5, FOREVER),
])
def test_limit_maxlife_unlimited(app_unlimited, secs, expected):
    with app_unlimited.app_context():
        assert limit_maxlife(secs) == expected


def test_allowed_units(app, app_unlimited):
    with app.app_context():
        assert allowed_maxlife_units() == ['minutes', 'hours', 'days', 'weeks']
    with app_unlimited.app_context():
        assert allowed_maxlife_units() == ['minutes', 'hours', 'days', 'weeks', 'months', 'years', 'forever']


def stored_maxlife(app, location):
    name = location.split('#')[0].rsplit('/', 1)[-1]
    with app.app_context():
        with app.storage.open(name) as item:
            return item.meta[TIMESTAMP_MAX_LIFE]


@pytest.mark.parametrize('value, unit, expected', [
    ('1', 'DAYS', DAY),
    ('1', 'FOREVER', 2 * WEEK),
    ('1', 'YEARS', 2 * WEEK),
])
def test_upload_is_limited(app, value, unit, expected):
    with app.test_client() as client:
        now = time.time()
        data = {'text': 'x', 'filename': 'x.txt', 'maxlife-value': value, 'maxlife-unit': unit}
        rv = client.post('/+upload', data=data)
        assert rv.status_code == 302
        assert stored_maxlife(app, rv.headers['Location']) == pytest.approx(now + expected, abs=5)


def test_index_offers_allowed_units_only(app):
    with app.test_client() as client:
        html = client.get('/').get_data(as_text=True)
    assert 'value="weeks"' in html
    assert 'value="months"' not in html
    assert 'value="forever"' not in html
    assert 'limited to the maximum' in html


def test_index_unlimited(app_unlimited):
    with app_unlimited.test_client() as client:
        html = client.get('/').get_data(as_text=True)
    assert 'value="forever"' in html
    assert 'limited to the maximum' not in html
