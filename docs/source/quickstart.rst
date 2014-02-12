Quickstart
==========

Installing bepasty
------------------

You can install bepasty either from PyPi (latest release) or from the git repository (latest available code).

::

    # from PyPi:
    pip install bepasty-server
    # from git repo
    pip install -e git+https://github.com/bepasty/bepasty-server.git#egg=bepasty-server


Starting bepasty server
-----------------------

You can run the bepasty server after installation with the following command.

::

    bepasty-server

The default configuration is to use the filesystem as storage location in /tmp.

.. warning::

    The default setting is that all files are unlocked.
    This means every user can upload and some other can download the file.
    If you host bepasty publicly you should set ``UPLOAD_UNLOCKED=False`` to avoid copyright issues.

The builtin WSGI server is recommended only for development and non-production use.

For production, you should use a WSGI server like gunicorn, apache+mod-wsgi, nginx+uwsgi, etc.

::

    gunicorn bepasty/wsgi.py
