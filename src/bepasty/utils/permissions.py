from flask import request, session, current_app
from flask import g as flaskg


# In the code, please always use these constants for permission values:
ADMIN = 'admin'
LIST = 'list'
CREATE = 'create'
MODIFY = 'modify'
READ = 'read'
DELETE = 'delete'

# Keys in the session:
PERMISSIONS = 'permissions'
LOGGEDIN = 'loggedin'

permission_icons = {
    'admin': 'user',
    'list': 'list',
    'create': 'plus',
    'modify': 'edit',
    'read': 'book',
    'delete': 'trash'
}


def lookup_permissions(token):
    """
    Look up the permissions string for the secret <token> in the configuration.
    If no such secret is configured, return None.
    """
    return current_app.config['PERMISSIONS'].get(token)


def get_permissions():
    """
    Get the permissions for the current user (if logged in)
    or the default permissions (if not logged in).
    """
    auth = request.authorization
    if auth:
        # HTTP Basic auth header present
        permissions = lookup_permissions(auth.password)
    elif 'token' in request.values:
        # Token present in query args or POST form (can be used by CLI clients)
        permissions = lookup_permissions(request.values['token'])
    else:
        # Look into the session; login might have put something there
        permissions = session.get(PERMISSIONS)
    if permissions is None:
        permissions = current_app.config['DEFAULT_PERMISSIONS']
    permissions = set(permissions.split(','))
    return permissions


def get_permission_icons():
    return [
        (permission, permission_icons[permission])
        for permission in sorted(get_permissions()) if permission
    ]


def may(permission):
    """
    Check whether the current user has the permission <permission>.
    """
    return permission in flaskg.permissions


def logged_in():
    """
    Is the user logged in?
    """
    return session.get(LOGGEDIN, False)
