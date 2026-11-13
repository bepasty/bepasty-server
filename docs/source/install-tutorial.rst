
=====================================================
Installation tutorial with Debian, Nginx and Gunicorn
=====================================================

This tutorial sets up bepasty on a Debian 13 ("trixie") server: Gunicorn runs
the bepasty WSGI app, Supervisor keeps Gunicorn running and Nginx is the
web server in front of it.

Replace ``bepasty.example.org`` with the DNS name of your server everywhere below.

Some steps are done as root, others as the user ``bepasty``. Each section says which.


Packages and system user (as root)
==================================

::

  apt install git python3-venv nginx supervisor

  # add the user bepasty (without a password, we will use "su - bepasty" as root)
  adduser --disabled-password --comment bepasty bepasty

  # Nginx (user www-data) needs to reach the Gunicorn socket and the static
  # files in /home/bepasty, which is only accessible by its owner by default.
  # Allow others to access paths in it, but not to list its content:
  chmod 711 /home/bepasty


Install bepasty (as user bepasty)
=================================

::

  # change to user bepasty
  su - bepasty
  # clone repository from GitHub
  git clone https://github.com/bepasty/bepasty-server.git repo
  # create folder for storage
  mkdir -m 700 storage
  # create a virtual environment
  python3 -m venv venv
  # install bepasty (with Pillow for image thumbnails) and Gunicorn (with gevent) into it
  venv/bin/pip install -e './repo[pillow]' 'gunicorn[gevent]'

Create the config file ``/home/bepasty/bepasty.conf``.

bepasty first loads its built-in defaults (see ``repo/src/bepasty/config.py``
or the :doc:`quickstart` section) and then the settings from this file, so it only
needs to contain the settings you want to change. Note that it uses plain
top-level ``KEY = value`` lines, there is no ``class Config`` in it:

::

  SITENAME = 'bepasty.example.org'

  # a long, random, secret string - you never need to type it in anywhere
  SECRET_KEY = 'replace this with a long random string'

  STORAGE = 'filesystem'
  STORAGE_FILESYSTEM_DIRECTORY = '/home/bepasty/storage/'

  # we use plain HTTP in this tutorial, see the HTTPS section below.
  SESSION_COOKIE_SECURE = False

  # the secret you use to log in at the web UI and what you may do then
  PERMISSIONS = {
      'replace this with your admin secret': 'admin,list,create,modify,read,delete',
  }
  # what users that are not logged in may do ('' = nothing, 'read' = read-only)
  DEFAULT_PERMISSIONS = ''

If you need a random string, you can use e.g.
``python3 -c 'import secrets; print(secrets.token_urlsafe(32))'``.

The config file contains secrets, so make it only readable for the bepasty user
and then go back to root:

::

  chmod 600 bepasty.conf
  exit


Supervisor and Gunicorn (as root)
=================================

Create ``/etc/supervisor/conf.d/bepasty.conf``:

::

  [program:bepasty]
  command = /home/bepasty/venv/bin/gunicorn bepasty.wsgi
      --name bepasty
      --workers 3
      --worker-class gevent
      --bind unix:/home/bepasty/gunicorn.sock
  environment = BEPASTY_CONFIG="/home/bepasty/bepasty.conf"
  directory = /home/bepasty
  user = bepasty
  stdout_logfile = /var/log/supervisor/bepasty.log
  redirect_stderr = true

Load it and check that bepasty is ``RUNNING``:

::

  supervisorctl update
  supervisorctl status bepasty


Nginx (as root)
===============

Create ``/etc/nginx/conf.d/bepasty.conf``:

::

  upstream bepasty_server {
    server unix:/home/bepasty/gunicorn.sock fail_timeout=0;
  }

  server {
    listen 80;
    listen [::]:80;
    server_name bepasty.example.org;  # <-- add your domain name here

    access_log /var/log/nginx/bepasty-access.log;
    error_log /var/log/nginx/bepasty-error.log;

    # must be bigger than MAX_BODY_SIZE in the bepasty config
    client_max_body_size 32M;

    location / {
        proxy_set_header Host $http_host;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_pass http://bepasty_server;
    }

    location /static/ {
        alias /home/bepasty/repo/src/bepasty/static/;
    }
  }

If this server only runs bepasty, also disable the Debian default site, which
otherwise answers all requests that do not use your domain name:

::

  rm /etc/nginx/sites-enabled/default

Check the configuration and reload Nginx:

::

  nginx -t
  systemctl reload nginx

Now open ``http://bepasty.example.org`` in your browser, log in with your admin
secret and upload a file.


HTTPS
=====

This tutorial uses plain HTTP to keep it short. For a server reachable from the
internet, you should use HTTPS, for example with a Let's Encrypt certificate
(Debian package ``python3-certbot-nginx``).

When bepasty is only reachable via HTTPS, set ``SESSION_COOKIE_SECURE = True``
in ``/home/bepasty/bepasty.conf`` and restart bepasty:
``supervisorctl restart bepasty``.

Nginx terminates HTTPS and talks plain HTTP to bepasty, so bepasty would generate
``http://`` URLs (e.g. for the QR code of an item). To use the scheme the client
used (sent by Nginx in the ``X-Forwarded-Proto`` header, see the Nginx
configuration above), also add this to ``/home/bepasty/bepasty.conf``:

::

  PROXY_FIX = {'x_proto': 1}


Updating bepasty
================

::

  su - bepasty
  git -C repo pull
  venv/bin/pip install -e './repo[pillow]'
  exit
  supervisorctl restart bepasty


Troubleshooting
===============

::

  supervisorctl status bepasty
  less /var/log/supervisor/bepasty.log
  less /var/log/nginx/bepasty-error.log
  less /var/log/nginx/bepasty-access.log

* ``502 Bad Gateway`` from Nginx: Gunicorn is not running (check the bepasty log)
  or Nginx can not access ``/home/bepasty/gunicorn.sock`` (check the permissions
  set up at the beginning).
* You can not log in: check ``SECRET_KEY`` (must not be empty) and
  ``SESSION_COOKIE_SECURE`` (must be ``False`` if you use HTTP).
* bepasty only reads its config at startup, so restart it after changing
  the config: ``supervisorctl restart bepasty``.
