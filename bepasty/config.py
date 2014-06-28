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

    #: server secret key needed for secure cookies
    #: you must set a very long, very random, very secret string here,
    #: otherwise bepasty will not work (and crash when trying to log in)!
    SECRET_KEY = ''

    #: not logged-in users get these permissions
    #: usually either nothing ('') or read-only ('read'):
    DEFAULT_PERMISSIONS = ''

    #: logged-in users may get more permissions
    #: you need a login secret to log in and, depending on that secret, you will
    #: get the configured permissions.
    #: you can use same secret / same permissions for all privileged users or
    #: set up different secrets / different permissions.
    #: PERMISSIONS is a dict that maps secrets to permissions, use it like:
    #: PERMISSIONS = {
    #:     'myadminsecret': 'admin,create,read,delete',
    #:     'myuploadersecret': 'create,read',
    #: }
    PERMISSIONS = {
    }
