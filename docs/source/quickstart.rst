Quickstart
==========

Installing Bepasty
------------------

You can install Bepasty either from PyPI (latest release) or from the Git repository (latest available code).

::

    # from PyPI:
    pip install bepasty

    # if you'd like to have python-magic help determine files' MIME types, use:
    pip install bepasty[magic]

    # from Git repository
    pip install -e git+https://github.com/bepasty/bepasty-server.git#egg=bepasty-server

Configuring Bepasty
-------------------
Before you can use bepasty, you need to carefully configure it (it won't work in default configuration and most of
the configuration settings need your attention).

When setting up permissions and giving out login secrets, carefully think about whom you give which permissions,
especially when setting up the ``DEFAULT_PERMISSIONS`` (which apply to not-logged-in users).

Here is the documentation straight from its config:

.. autoclass:: bepasty.config.Config
   :members:


To create a local configuration, create a file, e.g. ``/srv/bepasty/bepasty.conf``.
bepasty first loads the defaults shown above and then the settings from that file,
so it only needs to contain the settings you want to change:

::

    # Note: no Config class required, just simple KEY = value lines:
    SECRET_KEY = '........................'
    STORAGE = 'filesystem'
    STORAGE_FILESYSTEM_DIRECTORY = '/srv/bepasty/storage/'
    # ...


Important notes:

* if you copy settings from ``bepasty/config.py``, do not copy the
  "class Config" line and outdent the settings: due to how flask config files
  work, you need global KEY = VALUE statements on the top level of the config file.
* if you run over http (like for trying it locally / for development), you
  need to change the configuration to use SESSION_COOKIE_SECURE = False
  (otherwise you can not login as it won't transmit the cookie over unsecure
  http).


Starting the Bepasty server
---------------------------

You can run the bepasty server with your local configuration by pointing to it via the BEPASTY_CONFIG
environment variable like this:

::

    BEPASTY_CONFIG=/srv/bepasty/bepasty.conf bepasty-server

Important note:

* Use an absolute path as value for BEPASTY_CONFIG.


The built-in WSGI server is recommended only for development and non-production use.

For production, you should use a WSGI server like Gunicorn, Apache + mod_wsgi, Nginx + uWSGI, etc.

::

    gunicorn bepasty.wsgi


Invoking CLI commands
---------------------

All Bepasty commands expect either a --config <configfilename> argument or that the BEPASTY_CONFIG environment
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

The given criteria are combined (AND), at least one criterion is required.

bepasty removes items whose maximum lifetime is over when they get accessed or when the file list is shown.
To also remove expired items nobody accessed, run this regularly (e.g. as a cron job):

::

    bepasty-object purge --expired '*'


If you upgraded bepasty, you might need to upgrade the stored metadata to the current bepasty metadata schema:

::

    bepasty-object migrate '*'


Note: the '*' needs to be quoted with single-quotes so the shell does not expand it. it tells the command to operate
on all names in the storage (you could also give some specific names instead of '*').
