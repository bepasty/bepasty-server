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

    gunicorn bepasty.wsgi


Invoking CLI commands
---------------------

The "object" command operates on objects stored in the storage. You can get infos about them ("info" subcommand),
you can set some flags on them ("set"), you can remove all or some ("purge"), you can check the consistency
("consistency"), etc...

To get help about the object command, use:

::

    python -m bepasty.cli.object --help


To get help about the object purge subcommand, use:

::

    python -m bepasty.cli.object purge --help


To run the object purge subcommand (here: dry-run == do not remove anything, files >= 10MiB AND age >= 14 days),
use something like:

::

    python -m bepasty.cli.object purge --dry-run --size 10 --age 14 ../config.py '*'

Note: the '*' needs to be quoted with single-quotes so the shell does not expand it. it tells the command to operate
on all names in the storage (you could also give some specific names instead of '*').
