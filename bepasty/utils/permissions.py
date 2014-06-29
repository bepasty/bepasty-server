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


def may(permission):
    """
    check whether the current user has the permission <permission>
    """
    permissions = session.get(PERMISSIONS)
    if permissions is None:
        permissions = current_app.config['DEFAULT_PERMISSIONS']
    permissions = permissions.split(',')
    return permission in permissions


def logged_in():
    """
    is the user logged-in?
    """
    return session.get(LOGGEDIN, False)
