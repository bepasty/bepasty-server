# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.


class Config(object):
    """This is the basic configuration class for bepasty."""

    UPLOAD_UNLOCKED = True
    """
    .. warning::
        Uploads are default unlocked. Actually the admin should manual
        unlock the uploaded files to avoid copyright issues. In hosted
        version you should set ``UPLOAD_UNLOCKED = False``.
    """

    #: Set max content length
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

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
