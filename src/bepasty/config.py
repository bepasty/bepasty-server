class Config(object):
    """
    This is the basic configuration class for bepasty.

    IMPORTANT:

    The config is only loaded at startup time of the app, so if you change it,
    you need to restart the wsgi app process(es) to make it load the updated
    config.
    """

    #: name of this site (put YOUR bepasty fqdn here)
    SITENAME = 'bepasty.example.org'

    #: base URL path of app (if not served on root URL, but e.g. on http://example.org/bepasty ).
    #: setting this to a non-None value will activate the PrefixMiddleware that splits PATH_INFO
    #: into SCRIPT_NAME (== APP_BASE_PATH) and the rest of PATH_INFO.
    APP_BASE_PATH = None  # '/bepasty'

    #: Whether files are automatically locked after upload.
    #:
    #: If you want to require admin approval and manual unlocking for each
    #: uploaded file, set this to True.
    UPLOAD_LOCKED = False

    #: The asciinema player theme (one of asciinema, tango, solarized-dark,
    #: solarized-light, monokai)
    ASCIINEMA_THEME = 'asciinema'

    #: The site admin can set some maximum allowed file size he wants to
    #: accept here. This is the maximum size an uploaded file may have.
    MAX_ALLOWED_FILE_SIZE = 5 * 1000 * 1000 * 1000

    #: The maximum http request body size.
    #: This is an information given to rest api clients so they can adjust
    #: their chunk size accordingly.
    #:
    #: This needs to be in sync with (or at least not beyond) the web server
    #: settings:
    #: apache:  LimitRequestBody 1048576 # apache default is 0 (unlimited)
    #: nginx:  client_max_body_size 1m; # nginx default (== 1048576)
    MAX_BODY_SIZE = 1 * 1024 * 1024 - 8192  # 8kiB safety margin, issue #155

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

    # Whether to use the python-magic module to guess a file's mime
    # type by looking into its content (if the mime type can not be
    # determined from the filename extension).
    # NOTE:
    # libmagic may have security issues, so maybe you should only use
    # it if you trust all users with upload permissions ('create').
    USE_PYTHON_MAGIC = False

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

    #: Bepasty does **not** use the usual user/password scheme, but **only**
    #: uses passwords (or passphrases - we'll call both "a secret" below) as
    #: log-in credentials - there are no separate user names.
    #:
    #: People who log-in using such a secret may get more permissions than
    #: those who do not log-in (who just get DEFAULT_PERMISSIONS).
    #:
    #: Depending on the secret used to log-in, they will get the permissions
    #: configured here, see below.
    #:
    #: You can use same secret / same permissions for all privileged users or
    #: set up different secrets / different permissions for each user.
    #:
    #: If you want to be able to revoke permissions for some user / some group
    #: of users, it might be a good idea to remember to whom you gave which
    #: secret (and also handle it in a rather fine-grained way).
    #:
    #: PERMISSIONS is a dict that maps secrets to permissions, use it like:
    #:
    #: ::
    #:
    #:     PERMISSIONS = {
    #:         'myadminsecret_1.21d-3!wdar34': 'admin,list,create,modify,read,delete',
    #:         'uploadersecret_rtghtrbrrrfsd': 'create,read',
    #:         'joe_doe_89359299887711335537': 'create,read,delete',
    #:     }
    PERMISSIONS = {
        # 'foo': 'admin,list,create,modify,read,delete',
    }

    #: not-logged-in users get these permissions -
    #: usually they are either no permissions ('') or read-only ('read').
    DEFAULT_PERMISSIONS = ''
