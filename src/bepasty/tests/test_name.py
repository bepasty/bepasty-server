import pytest

from bepasty.utils.name import ItemName, encode, make_id


def test_create():
    fake_storage = {}
    n = ItemName.create(fake_storage)
    assert n


def test_create_many():
    fake_storage = {}
    length = 1
    count = 400  # way more than we can do with this name length
    max_seen_length = 0
    for i in range(count):
        name = ItemName.create(fake_storage, length=length, max_length=length * 4, max_tries=10)
        # use the name in storage, so it is not available any more
        fake_storage[name] = None
        max_seen_length = max(max_seen_length, len(name))
    # it should automatically use longer names, if it runs out of unique names:
    assert max_seen_length > length
    # we should get all unique names we wanted, no duplicates:
    assert len(list(fake_storage)) == count


def test_make_id_type():
    assert isinstance(make_id(2), str)


def test_make_id_length():
    for length in range(10):
        assert len(make_id(length)) == length


def test_make_id_alphabet():
    # id must contain alphabet chars ONLY
    assert set(make_id(10, alphabet="abc")) <= set(['a', 'b', 'c'])


def test_make_id_unique():
    length, count = 6, 10000
    ids = set(make_id(length) for i in range(count))
    # if we did not encounter duplicates, set size must be <count>
    # of course, in extremely rare cases, this test might fail
    assert len(ids) == count


def test_encode_length():
    length = 42
    assert len(encode(12345, length)) == length


def test_encode_binary():
    assert encode(0, 0, "01") == []  # zero length
    assert encode(1, 0, "01") == []  # zero length
    assert encode(0, 1, "01") == ['0']  # length match
    assert encode(1, 1, "01") == ['1']  # length match
    assert encode(0, 2, "01") == ['0', '0']  # leading zeroes
    assert encode(1, 2, "01") == ['0', '1']  # leading zeroes
    assert encode(2, 2, "01") == ['1', '0']  # length match
    assert encode(3, 2, "01") == ['1', '1']  # length match
    assert encode(4, 2, "01") == ['0', '0']  # overflow truncated


def test_encode_special():
    # equivalent to binary, but we see the code is rather flexible
    assert encode(0, 2, ".+") == ['.', '.']
    assert encode(1, 2, ".+") == ['.', '+']
    assert encode(2, 2, ".+") == ['+', '.']
    assert encode(3, 2, ".+") == ['+', '+']


def test_encode_decimal():
    assert encode(123, 3, "0123456789") == ['1', '2', '3']  # length match
    assert encode(456, 4, "0123456789") == ['0', '4', '5', '6']  # leading zeroes
    assert encode(7890, 3, "0123456789") == ['8', '9', '0']  # overflow truncated


def test_encode_hex():
    assert encode(31, 2, "0123456789ABCDEF") == ['1', 'F']


def test_encode_errors():
    with pytest.raises(ValueError):  # ValueError: alphabet must be at least 2 elements long
        encode(1, 1, "0")

    with pytest.raises(ValueError):  # ValueError: length must be >= 0
        encode(1, -1, "0")

    with pytest.raises(ValueError):  # ValueError: negative values are not supported
        encode(-1, 1, "0")
