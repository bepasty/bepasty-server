from bepasty.storage.filesystem import Item


def test(tmpdir):
    pm = tmpdir.join("test.meta")
    pd = tmpdir.join("test.data")

    with Item(pm.open('w+b'), pd.open('w+b')) as i:
        assert i.data is not None
        assert i.meta is not None
