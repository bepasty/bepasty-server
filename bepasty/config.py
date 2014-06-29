# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.


class Config(object):
    """This is the basic configuration class for bepasty."""

    #: name of this site (put YOUR bepasty fqdn here)
    SITENAME = 'bepasty.example.org'

    #: Whether files are automatically locked after upload.
    #:
    #: If you want to require admin approval and manual unlocking for each
    #: uploaded file, set this to True.
    UPLOAD_LOCKED = False

    #: Define storage backend, choose from:
    #:
    #: - 'filesystem'
    #: - 'ceph'
    #:
    #: Note: ceph storage currently lacks names-in-storage iteration, see
    #: issue #38. Thus we recommend using filesystem storage currently.
    STORAGE = 'filesystem'

    #: Filesystem storage path
    STORAGE_FILESYSTEM_DIRECTORY = '/tmp/'

    #: Config file for CEPH storage
    STORAGE_CEPH_CONFIG_FILE = '/etc/ceph/ceph.conf'
    #: CEPH pool name for actually data
    STORAGE_CEPH_POOL_DATA = 'bepasty-data'
    #: CEPH pool name for meta data
    STORAGE_CEPH_POOL_META = 'bepasty-meta'

    #: server secret key needed for secure cookies.
    #: you must set a very long, very random, very secret string here,
    #: otherwise bepasty will not work (and crash when trying to log in)!
    SECRET_KEY = ''

    #: not-logged-in users get these permissions -
    #: usually they are either no permissions ('') or read-only ('read').
    DEFAULT_PERMISSIONS = ''

    #: logged-in users may get more permissions.
    #: a user may have a login secret to log in and, depending on that secret,
    #: he/she will get the permissions configured here.
    #:
    #: you can use same secret / same permissions for all privileged users or
    #: set up different secrets / different permissions for each user.
    #:
    #: PERMISSIONS is a dict that maps secrets to permissions, use it like:
    #:
    #: ::
    #:
    #:     PERMISSIONS = {
    #:         'myadminsecret': 'admin,create,read,delete',
    #:         'uploadersecret': 'create,read',
    #:     }
    PERMISSIONS = {
         #'foo': 'admin,create,read,delete',
    }
