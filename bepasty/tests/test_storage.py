import pytest

from bepasty.storage.filesystem import Storage


def test_contains(tmpdir):
    storage = Storage(str(tmpdir))
    name = "foo"
    # check if it is not there yet
    assert name not in storage
    with storage.create(name, 0):
        # we just want it created, no need to write sth into it
        pass
    # check if it is there
    assert name in storage
    storage.remove(name)
    # check if it is gone
    assert name not in storage


def test_iter(tmpdir):
    storage = Storage(str(tmpdir))
    # nothing there yet
    assert list(storage) == []
    names = ["foo", "bar", "baz", ]
    for name in names:
        with storage.create(name, 0):
            # we just want it created, no need to write sth into it
            pass
    assert set(list(storage)) == set(names)


def test_invalid_name(tmpdir):
    storage = Storage(str(tmpdir))
    name = "../invalid"
    with pytest.raises(RuntimeError):
        storage.create(name, 0)
