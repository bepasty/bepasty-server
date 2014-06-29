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


Configuring bepasty
-------------------
Before you can use bepasty, you need to carefully configure it (it won't work in default configuration and most of
the configuration settings need your attention).

When setting up permissions and giving out login secrets, carefully think about whom you give which permissions,
especially when setting up the ``DEFAULT_PERMISSIONS`` (which apply to not-logged-in users).

Here is the documentation straight from its config:

.. autoclass:: bepasty.config.Config
   :members:


To create a local and non-default configuration, copy ``bepasty/config.py`` to e.g. ``/srv/bepasty/bepasty.conf``
first, then modify it:

::

    # Note: no Config class required, just simple KEY = value lines:
    SECRET_KEY = '........................'
    STORAGE = 'filesystem'
    STORAGE_FILESYSTEM_DIRECTORY = '/srv/bepasty/storage/'
    # ...


Starting bepasty server
-----------------------

You can run the bepasty server with your local configuration by pointing to it via the BEPASTY_CONFIG
environment variable like this:

::

    BEPASTY_CONFIG=/srv/bepasty/bepasty.conf bepasty-server


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


If you upgraded bepasty, you might need to upgrade the stored metadata to the current bepasty metadata schema:

::

    python -m bepasty.cli.object migrate ../config.py '*'


Note: the '*' needs to be quoted with single-quotes so the shell does not expand it. it tells the command to operate
on all names in the storage (you could also give some specific names instead of '*').
