# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.


class Config(object):
    # Uploads are normaly locked and must first unlock the file
    UPLOAD_UNLOCKED = False

    # Set max content length
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024

    # Define storage module
    # Available:
    # - filesystem
    # - ceph
    STORAGE = 'filesystem'

    # Filesystem storage specific config
    STORAGE_FILESYSTEM_DIRECTORY = '/tmp/'

    # CEPH storage specific config
    STORAGE_CEPH_CONFIG_FILE = '/etc/ceph/ceph.conf'
    STORAGE_CEPH_POOL_DATA = 'bepasty-data'
    STORAGE_CEPH_POOL_META = 'bepasty-meta'
