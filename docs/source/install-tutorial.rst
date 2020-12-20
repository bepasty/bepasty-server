
=====================================================
Installation tutorial with Debian, NGinx and gunicorn
=====================================================

Following this tutorial you'll have a running Debian+Nginx+gunicorn+bepasty (HTTP) instance using Python3 on a minimally installed Debian server.  It is strongly recommended to use HTTPS for Internet facing services - configuring Nginx for HTTPS is left to the reader.

After installing a minimal Debian 10 server.

Install preliminary required packages:

::

  apt-get install nginx git-core python3-dev python3-pip virtualenv python3-virtualenv


Some commands need to be run as root - others as the user bepasty.

Commands to run as root:

::

  # add user bepasty to system
  adduser bepasty --disabled-login
  # add path to bepasty/.bash_rc
  echo 'export PATH="/home/bepasty/.local/bin:$PATH"' >> /home/bepasty/.bash_rc
  
Commands to run as user bepasty:

::

  # change to user bepasty
  sudo su - bepasty
  # clone repository from github
  git clone https://github.com/bepasty/bepasty-server.git repo
  # create folder for storage
  mkdir storage
  # create folder for logs
  mkdir logs
  # create virtualenv
  virtualenv .
  # activate virtualenv
  . bin/activate
  cd repo
  # install bepasty and requirements
  pip3 install -e .
  # add gunicorn and gevent for hosting
  pip3 install gunicorn gevent

Config file for bepasty -- ``/home/bepasty/bepasty.conf``:

Copy ``src/bepasty/config.py`` to ``/home/bepasty/bepasty.conf`` first,
remove the ``class Config`` and remove all indents in the file.
The comments can be removed too, if you feel the need to.

An easy way to do this in one go:

::

  # create trim alias
  alias trim="awk '{\$1=\$1};1'"
  # remove the top 11 lines + trim spaces at beginning of lines
  trim src/bepasty/config.py | tail -n +11 > /home/bepasty/bepasty.conf


At least modify these four config variables.  

::

  SITENAME = 'bepasty.example.org'
  STORAGE = 'filesystem'
  STORAGE_FILESYSTEM_DIRECTORY = '/home/bepasty/storage/'
  SESSION_COOKIE_SECURE = False

Add this content to ``/home/bepasty/bin/gunicorn_bepasty``:

::

  #!/bin/bash

  NAME="bepasty"
  HOME=/home/bepasty
  SOCKFILE=$HOME/gunicorn.sock  # we will communicate using this unix socket
  PIDFILE=$HOME/gunicorn.pid
  NUM_WORKERS=3                 # how many worker processes should Gunicorn spawn
  export PATH="/home/bepasty/.local/bin:$PATH"  #include gunicorn path for exec
  export BEPASTY_CONFIG=$HOME/bepasty.conf

  source $HOME/bin/activate

  cd $HOME/repo

  exec gunicorn bepasty.wsgi \
    --name $NAME \
    --workers $NUM_WORKERS \
    --log-level=info \
    --bind=unix:$SOCKFILE \
    --pid $PIDFILE \
    -k gevent

Make it executable: ``chmod +x ~/bin/gunicorn_bepasty``

Commands to run as root:
  
A nginx configuration i.e. in ``/etc/nginx/conf.d/bepasty.conf``:

At least modify the server_name variable:

::

  upstream pasty_server {
    server unix:/home/bepasty/gunicorn.sock fail_timeout=0;
  }

  server {
    listen 80;
    #listen [::]:80; #uncomment this if your server supports IPv6
    server_name bepasty.example.org;  # <-- add your domainname here

    access_log /home/bepasty/logs/nginx-access.log;
    error_log /home/bepasty/logs/nginx-error.log;

    client_max_body_size 32M;

    location / {
        proxy_set_header Host $http_host;
        proxy_pass http://pasty_server;
    }

    location /static/ {
        alias /home/bepasty/repo/src/bepasty/static/;
    }
  }

Now reload your nginx configuration: `service nginx reload`.  

Supervisord config i.e. in ``/etc/supervisor/conf.d/bepasty.conf``:

::

  [program:bepasty]
  command = /home/bepasty/bin/gunicorn_bepasty                  ; Command to start app
  user = bepasty                                                ; User to run as
  stdout_logfile = /home/bepasty/logs/gunicorn_supervisor.log   ; Where to write log messages
  redirect_stderr = true                                        ; Save stderr in the same log

Finally reload supervisor: `service supervisor reload`

In your browser go to your server address: ``http://bepasty.example.org``

You should now have a running bepasty server on port 80 (HTTP) of your server.

Places to look when troubleshooting:

::

  journalctl -u nginx.service
  journalctl -u supervisor.service
  tail /home/bepasty/logs/nginx-access.log
  tail /home/bepasty/logs/nginx-error.log
  tail /home/bepasty/logs/gunicorn_supervisor.log

Important notes:

* If you copied the file from the ``bepasty/config.py`` it will have
  a "class Config" in it and all the settings are inside that class. This is
  **not** what you need. Due to how flask config files work, you need to
  remove the class statement and outdent all the settings, so you just have
  global KEY = VALUE statements left on the top level of the config file.
* When adding additional users in ``bepasty/config.py`` make sure you have
  ``'user_secret': 'correct,list,of,permissions',``
  any missing ``'' : '',`` will result in the bepasty server not starting.
  
Tips & Tricks:

* The user secret in ``bepasty/config.py`` needs to be secure - an easy way 
  to create secure random character strings on the command line is:
  ``tr -dc A-Za-z0-9 </dev/urandom | head -c 10 ; echo ''``
  this can also be used to create a long random secure SECRET_KEY value:
  ``tr -dc 'A-Za-z0-9!"#$%&'\''()*+,-./:;<=>?@[\]^_`{|}~' </dev/urandom | head -c 255  ; echo ''``
