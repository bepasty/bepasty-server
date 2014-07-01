# Copyright: 2014 Thomas Waldmann <tw@waldmann-edv.de>
# License: BSD 2-clause, see LICENSE for details.

from flask import session, current_app

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
    permissions = session.get(PERMISSIONS)
    if permissions is None:
        permissions = current_app.config['DEFAULT_PERMISSIONS']
    return permissions


def may(permission):
    """
    check whether the current user has the permission <permission>
    """
    permissions = get_permissions().split(',')
    return permission in permissions


def logged_in():
    """
    is the user logged-in?
    """
    return session.get(LOGGEDIN, False)
