from .name import ItemName

def test_create():
    n = ItemName.create()
    assert n

def test_parse():
    n = ItemName.parse('e44f1baa-d23f-4f5f-bd75-37bc3286ef7a')
    assert n == 'e44f1baa-d23f-4f5f-bd75-37bc3286ef7a'
    n = ItemName.parse('e44f1baad23f4f5fbd7537bc3286ef7a')
    assert n == 'e44f1baa-d23f-4f5f-bd75-37bc3286ef7a'
