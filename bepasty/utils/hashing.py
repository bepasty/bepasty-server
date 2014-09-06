from hashlib import sha256 as hash_new

SIZE = 1024 * 1024


def compute_hash(data, size):
    """
    compute hash of storage item's data file, return hexdigest
    """
    hasher = hash_new()
    offset = 0
    while offset < size:
        buf = data.read(SIZE, offset)
        offset += len(buf)
        hasher.update(buf)
    return hasher.hexdigest()
