import tempfile

from . import Item

def test():
    f1 = tempfile.TemporaryFile()
    f2 = tempfile.TemporaryFile()

    i = Item(f1, f2)
    assert i.data is not None
    assert i.meta is not None
