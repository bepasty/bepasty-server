from bepasty.storage.filesystem import Meta


def test(tmpdir):
    p = tmpdir.join("test.meta")

    m = Meta(p.open('w+b'))
    assert len(m) == 0
    m.close()

    m = Meta(p.open('r+b'))
    m['flag'] = True
    assert len(m) == 1
    m.close()

    m = Meta(p.open('r+b'))
    assert len(m) == 1
    assert m['flag'] is True
    m.close()


def test_iter(tmpdir):
    p = tmpdir.join("test.meta")

    m = Meta(p.open('w+b'))
    keys = ["foo", "bar", "baz", ]
    for key in keys:
        m[key] = True
    m.close()

    m = Meta(p.open('r+b'))
    assert set(list(m)) == set(keys)
    m.close()


def test_del(tmpdir):
    p = tmpdir.join("test.meta")
    key = "foo"

    m = Meta(p.open('w+b'))
    m[key] = True
    m.close()

    m = Meta(p.open('r+b'))
    del m[key]
    m.close()

    m = Meta(p.open('r+b'))
    assert len(m) == 0
    assert key not in m
    m.close()
