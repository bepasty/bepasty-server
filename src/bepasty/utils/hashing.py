from hashlib import sha256 as hash_new

SIZE = 1024 * 1024


def compute_hash(data, size):
    """
    Compute the SHA-256 hash of a storage item's data file and return the hex digest.

    :param data: storage data object with a read(length, offset) method
    :param size: total number of bytes to read and hash
    :return: hexadecimal digest string
    """
    hasher = hash_new()
    offset = 0
    while offset < size:
        buf = data.read(SIZE, offset)
        offset += len(buf)
        hasher.update(buf)
    return hasher.hexdigest()
