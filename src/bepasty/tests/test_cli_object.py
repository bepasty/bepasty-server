import time

import pytest

from bepasty.cli.object import Main
from bepasty.constants import (
    FILENAME,
    FOREVER,
    SIZE,
    TIMESTAMP_DOWNLOAD,
    TIMESTAMP_MAX_LIFE,
    TIMESTAMP_UPLOAD,
    TYPE,
)
from bepasty.storage.filesystem import Storage

DAY = 24 * 3600
MiB = 1024 * 1024


def make_item(storage, name, *, age_days=0, size=1, max_life=FOREVER):
    now = int(time.time())
    with storage.create(name, 0) as item:
        item.meta[FILENAME] = name
        item.meta[SIZE] = size
        item.meta[TYPE] = 'text/plain'
        item.meta[TIMESTAMP_UPLOAD] = now - age_days * DAY
        item.meta[TIMESTAMP_DOWNLOAD] = 0
        item.meta[TIMESTAMP_MAX_LIFE] = max_life


def purge(storage, *args):
    args = Main.argparser.parse_args(['purge', *args, '*'])
    Main.check_purge_args(args)
    for name in list(storage):
        Main.do_purge(None, storage, name, args)


@pytest.fixture
def storage(tmpdir):
    storage = Storage(str(tmpdir))
    now = int(time.time())
    make_item(storage, 'forever_old_big', age_days=30, size=20 * MiB, max_life=FOREVER)
    make_item(storage, 'valid_old_big', age_days=30, size=20 * MiB, max_life=now + DAY)
    make_item(storage, 'expired_new_small', age_days=0, size=1, max_life=now - 60)
    make_item(storage, 'forever_new_small', age_days=0, size=1, max_life=FOREVER)
    return storage


def test_purge_expired(storage):
    purge(storage, '--expired')
    assert set(storage) == {'forever_old_big', 'valid_old_big', 'forever_new_small'}


def test_purge_criteria_ignore_lifetime(storage):
    # items that have not expired (or never expire) must be purgeable by other criteria
    purge(storage, '--age', '14', '--size', '10')
    assert set(storage) == {'expired_new_small', 'forever_new_small'}


def test_purge_criteria_combined_with_expired(storage):
    purge(storage, '--age', '14', '--expired')
    assert set(storage) == {'forever_old_big', 'valid_old_big', 'expired_new_small', 'forever_new_small'}


def test_purge_dry_run(storage):
    purge(storage, '--dry-run', '--age', '0')
    assert len(set(storage)) == 4


def test_purge_requires_criterion(storage):
    with pytest.raises(SystemExit):
        purge(storage)
    with pytest.raises(SystemExit):
        purge(storage, '--dry-run')
    assert len(set(storage)) == 4
