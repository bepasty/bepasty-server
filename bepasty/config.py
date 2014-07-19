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

    #: The site admin can set some maximum allowed file size he wants to
    #: accept here. This is the maximum size an uploaded file may have.
    #:
    #: Keep this in sync with bepasty/static/app/js/fileuploader.js:
    #: maxFileSize: 5 * 1000 * 1000 * 1000
    MAX_ALLOWED_FILE_SIZE = 5 * 1000 * 1000 * 1000

    #: The maximum http request body size.
    #: This is an information given to rest api clients so they can adjust
    #: their chunk size accordingly.
    #:
    #: This needs to be in sync with (or at least not beyond) the web server
    #: settings:
    #: apache:  LimitRequestBody 1048576 # apache default is 0 (unlimited)
    #: nginx:  client_max_body_size 1m; # nginx default (== 1048576)
    #:
    #: Also, bepasty/static/app/js/fileuploader.js needs to be in sync (or
    #: at least not beyond the web server setting) , too:
    #: maxChunkSize: 1 * 1024 * 1024
    MAX_BODY_SIZE = 1 * 1024 * 1024

    #: Setup maximum file sizes for specific content-types. If an item is
    #: beyond the limit set for its type, it will not be rendered, but just
    #: offered for download. Lookup within MAX_RENDER_SIZE is done by
    #: first-match and it is automatically sorted for longer content-type-
    #: prefixes first.
    #:
    #: Format of entries: content-type-prefix: max_size
    MAX_RENDER_SIZE = {
        # each list entry has 38 bytes, do not render > 1000 items
        'text/x-bepasty-list': 1000 * 38,
        # stuff rendered with syntax highlighting (expensive for server and
        # client) and also used for other text/* types as we use same code to
        # get a (non-highlighted) display with line numbers:
        'HIGHLIGHT_TYPES': 100 * 1000,
        # the in-browser pdf reader is sometimes rather slow and should
        # rather not be used for big PDFs:
        'application/pdf': 10 * 1000 * 1000,
        'application/x-pdf': 10 * 1000 * 1000,
        # images / audio / video can be rather big, we do not process them:
        'image/': 10 * 1000 * 1000,
        'audio/': 1 * 1000 * 1000 * 1000,
        'video/': 5 * 1000 * 1000 * 1000,
        # DEFAULT - matches everything not matched otherwise.
        # As we have catched everything we are able to render already,
        # this maybe should be a medium size, just for the case we forget
        # something:
        '': 1 * 1000 * 1000,
    }

    #: Define storage backend, choose from:
    #:
    #: - 'filesystem'
    #:
    STORAGE = 'filesystem'

    #: Filesystem storage path
    STORAGE_FILESYSTEM_DIRECTORY = '/tmp/'

    #: server secret key needed for safe session cookies.
    #: you must set a very long, very random, very secret string here,
    #: otherwise bepasty will not work (and crash when trying to log in)!
    SECRET_KEY = ''

    #: transmit cookie only over https (if you use http, set this to False)
    SESSION_COOKIE_SECURE = True
    #: use a permanent session (True, cookie will expire after the given
    #: time, see below) or not (False, cookie will get removed when browser
    #: is closed)
    PERMANENT_SESSION = False
    #: lifetime of the permanent session (in seconds)
    PERMANENT_SESSION_LIFETIME = 31 * 24 * 3600

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
        # 'foo': 'admin,create,read,delete',
    }
