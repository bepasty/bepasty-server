Quickstart
==========

Installing bepasty
------------------

You can install bepasty either from PyPi (latest release) or from the git repository (latest available code).

::

    # from PyPi:
    pip install bepasty

    # if you'ld like to have python-magic to help determining files' mime types, use:
    pip install bepasty[magic]

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
first, remove the ``class Config`` and remove all indents in the file.
The comments can be removed too, if you feel the need to.
At last modify these two configs variables: then modify it:

::

    # Note: no Config class required, just simple KEY = value lines:
    SECRET_KEY = '........................'
    STORAGE = 'filesystem'
    STORAGE_FILESYSTEM_DIRECTORY = '/srv/bepasty/storage/'
    # ...


Important notes:

* if you copied the file from the ``bepasty/config.py`` it will have
  a "class Config" in it and all the settings are inside that class. This is
  **not** what you need. Due to how flask config files work, you need to
  remove the class statement and outdent all the settings, so you just have
  global KEY = VALUE statements left on the top level of the config file.
* if you run over http (like for trying it locally / for development), you
  need to change the configuration to use SESSION_SECURE_COOKIE = False
  (otherwise you can not login as it won't transmit the cookie over unsecure
  http).


Starting bepasty server
-----------------------

You can run the bepasty server with your local configuration by pointing to it via the BEPASTY_CONFIG
environment variable like this:

::

    BEPASTY_CONFIG=/srv/bepasty/bepasty.conf bepasty-server

Important note:

* Use an absolute path as value for BEPASTY_CONFIG.


The builtin WSGI server is recommended only for development and non-production use.

For production, you should use a WSGI server like gunicorn, apache+mod-wsgi, nginx+uwsgi, etc.

::

    gunicorn bepasty.wsgi


Invoking CLI commands
---------------------

All bepasty commands expect either a --config <configfilename> argument or that the BEPASTY_CONFIG environment
variable points to your configuration file.

The "object" command operates on objects stored in the storage. You can get infos about them ("info" subcommand),
you can set some flags on them ("set"), you can remove all or some ("purge"), you can check the consistency
("consistency"), etc...

To get help about the object command, use:

::

    bepasty-object --help


To get help about the object purge subcommand, use:

::

    bepasty-object purge --help


To run the object purge subcommand (here: dry-run == do not remove anything, files >= 10MiB AND age >= 14 days),
use something like:

::

    bepasty-object purge --dry-run --size 10 --age 14 '*'


If you upgraded bepasty, you might need to upgrade the stored metadata to the current bepasty metadata schema:

::

    bepasty-object migrate '*'


Note: the '*' needs to be quoted with single-quotes so the shell does not expand it. it tells the command to operate
on all names in the storage (you could also give some specific names instead of '*').
