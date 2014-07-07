# Copyright: 2014 Thomas Waldmann <tw@waldmann-edv.de>
# License: BSD 2-clause, see LICENSE for details.

from flask import request, session, current_app
from flask import g as flaskg


# in the code, please always use this constants for permission values:
ADMIN = 'admin'
CREATE = 'create'
READ = 'read'
DELETE = 'delete'

# key in the session:
PERMISSIONS = 'permissions'
LOGGEDIN = 'loggedin'


def get_permissions():
    """
    get the permissions for the current user (if logged in)
    or the default permissions (if not logged in).
    """
    auth = request.authorization
    if auth:
        # http basic auth header present
        permissions = current_app.config['PERMISSIONS'].get(auth.password)
    else:
        # look into session, login might have put something there
        permissions = session.get(PERMISSIONS)
    if permissions is None:
        permissions = current_app.config['DEFAULT_PERMISSIONS']
    permissions = set(permissions.split(','))
    return permissions


def may(permission):
    """
    check whether the current user has the permission <permission>
    """
    return permission in flaskg.permissions


def logged_in():
    """
    is the user logged-in?
    """
    return session.get(LOGGEDIN, False)
