import re
import time
import mimetypes
from werkzeug.exceptions import BadRequest, RequestEntityTooLarge

from flask import current_app

try:
    import magic as magic_module
    magic = magic_module.Magic(mime=True)
    magic_bufsz = magic.getparam(magic_module.MAGIC_PARAM_BYTES_MAX)
except ImportError:
    magic = None
    magic_bufsz = None

from ..constants import (
    COMPLETE,
    FILENAME,
    FOREVER,
    HASH,
    LOCKED,
    SIZE,
    TIMESTAMP_DOWNLOAD,
    TIMESTAMP_MAX_LIFE,
    TIMESTAMP_UPLOAD,
    TYPE,
    TYPE_HINT,
    internal_meta,
)
from .name import ItemName
from .decorators import threaded
from .hashing import compute_hash, hash_new

# we limit to 250 characters as we do not want to accept arbitrarily long
# filenames. other than that, there is no specific reason we could not
# also take more (or less).
MAX_FILENAME_LENGTH = 250


class Upload(object):
    _filename_re = re.compile(r'[^a-zA-Z0-9 *+:;.,_-]+')
    _type_re = re.compile(r'[^a-zA-Z0-9/+.-]+')

    @classmethod
    def filter_size(cls, i):
        """
        Filter size.
        Check for advertised size.
        """
        try:
            i = int(i)
        except (ValueError, TypeError):
            raise BadRequest(description='Size is invalid')
        if i > current_app.config['MAX_ALLOWED_FILE_SIZE']:
            raise RequestEntityTooLarge()
        return i

    @classmethod
    def filter_filename(cls, filename, storage_name, content_type, content_type_hint):
        """
        Filter filename.
        Only allow some basic characters and shorten to 50 characters.
        """
        # Make up filename if we don't have one
        if not filename:
            if not content_type:
                content_type = content_type_hint
            # note: stdlib mimetypes.guess_extension is total crap
            if content_type.startswith("text/"):
                ext = ".txt"
            else:
                ext = ".bin"
            filename = storage_name + ext
        return cls._filename_re.sub('', filename)[:MAX_FILENAME_LENGTH]

    @classmethod
    def filter_type(cls, ct, ct_hint, filename=None):
        """
        Filter Content-Type
        Only allow some basic characters and shorten to 50 characters.

        Return value:
        tuple[0] - content-type string
        tuple[1] - whether tuple[0] is hint or not
                   True:  content-type is just a hint
                   False: content-type is not a hint, was specified by user
        """
        if not ct and filename:
            ct, encoding = mimetypes.guess_type(filename)
        if not ct:
            return ct_hint, True
        return cls._type_re.sub('', ct)[:50], False

    @classmethod
    def meta_new(cls, item, input_size, input_filename, input_type,
                 input_type_hint, storage_name, maxlife_stamp=FOREVER):
        item.meta[FILENAME] = cls.filter_filename(
            input_filename, storage_name, input_type, input_type_hint
        )
        item.meta[SIZE] = cls.filter_size(input_size)
        ct, hint = cls.filter_type(input_type, input_type_hint, input_filename)
        item.meta[TYPE] = ct
        item.meta[TYPE_HINT] = hint
        item.meta[TIMESTAMP_UPLOAD] = int(time.time())
        item.meta[TIMESTAMP_DOWNLOAD] = 0
        item.meta[LOCKED] = current_app.config['UPLOAD_LOCKED']
        item.meta[COMPLETE] = False
        item.meta[HASH] = ''
        item.meta[TIMESTAMP_MAX_LIFE] = maxlife_stamp

    @classmethod
    def meta_complete(cls, item, file_hash):
        # update TYPE by python-magic if not decided yet
        if item.meta.pop(TYPE_HINT, False):
            if magic and current_app.config.get('USE_PYTHON_MAGIC', False):
                if item.meta[TYPE] == 'application/octet-stream':
                    item.meta[TYPE] = magic.from_buffer(item.data.read(magic_bufsz, 0))
        item.meta[COMPLETE] = True
        item.meta[HASH] = file_hash

    @staticmethod
    def data(item, f, size_input, offset=0):
        """
        Copy data from temp file into storage.
        """
        read_length = 16 * 1024
        size_written = 0
        hasher = hash_new()

        while True:
            read_length = min(read_length, size_input)
            if size_input == 0:
                break

            buf = f.read(read_length)
            if not buf:
                # Should not happen, we already checked the size
                raise RuntimeError

            item.data.write(buf, offset + size_written)
            hasher.update(buf)

            len_buf = len(buf)
            size_written += len_buf
            size_input -= len_buf

        return size_written, hasher.hexdigest()


def create_item(f, filename, size, content_type, content_type_hint,
                maxlife_stamp=FOREVER):
    """
    create an item from open file <f> with the given metadata, return the item name.
    """
    name = ItemName.create(current_app.storage)
    with current_app.storage.create(name, size) as item:
        size_written, file_hash = Upload.data(item, f, size)
        Upload.meta_new(item, size, filename, content_type, content_type_hint,
                        name, maxlife_stamp=maxlife_stamp)
        Upload.meta_complete(item, file_hash)
    return name


def filter_internal(meta):
    """
    filter internal meta data out.
    """
    return {k: v for k, v in meta.items() if k not in internal_meta}


@threaded
def background_compute_hash(storage, name):
    with storage.openwrite(name) as item:
        size = item.meta[SIZE]
        file_hash = compute_hash(item.data, size)
        item.meta[HASH] = file_hash
