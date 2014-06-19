# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.


class Config(object):
    """This is the basic configuration class for bepasty."""

    #: name of this site (put YOUR bepasty fqdn here)
    SITENAME = 'bepasty.example.org'

    UPLOAD_UNLOCKED = True
    """
    .. warning::
        Uploads are default unlocked. Actually the admin should manual
        unlock the uploaded files to avoid copyright issues. In hosted
        version you should set ``UPLOAD_UNLOCKED = False``.
    """

    #: Define storage module
    #: Available:
    #: - filesystem
    #: - ceph
    STORAGE = 'filesystem'

    #: Filesystem storage specific config
    STORAGE_FILESYSTEM_DIRECTORY = '/tmp/'

    #: Config file for CEPH storage
    STORAGE_CEPH_CONFIG_FILE = '/etc/ceph/ceph.conf'
    #: CEPH pool name for actually data
    STORAGE_CEPH_POOL_DATA = 'bepasty-data'
    #: CEPH pool name for meta data
    STORAGE_CEPH_POOL_META = 'bepasty-meta'

    SECRET_KEY = 'verylongsecretstringneededforsessionstorage'  # XXX change this!

    #: secret "login" tokens to be able to login (required to be able to upload files)
    #: you can use same token for all uploaders (shared secret) or give each uploader
    #: an individual token (easier to revoke).
    #: note: downloading does not require logging in, everybody who knows the download
    #: url of a file may download it.
    TOKENS = {  # change these!
        'usetheforceluke',
        'foobar',
    }
