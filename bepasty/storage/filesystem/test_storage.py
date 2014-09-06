from . import Storage


def test_contains(tmpdir):
    storage = Storage(str(tmpdir))
    name = "foo"
    # check if it is not there yet
    assert name not in storage
    with storage.create(name, 0) as item:
        # we just want it created, no need to write sth into it
        pass
    # check if it is there
    assert name in storage
    storage.remove(name)
    # check if it is gone
    assert name not in storage
