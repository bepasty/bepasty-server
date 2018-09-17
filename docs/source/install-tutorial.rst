
=====================================================
Installation tutorial with Debian, NGinx and gunicorn
=====================================================

preliminary packages:

::

  apt-get install build-essential nginx supervisor python-dev git-core python-pip python-virtualenv


commands to run

::

  # add user bepasty to system
  adduser bepasty
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
  pip install -e .
  # add gunicorn and gevent for hosting
  pip install gunicorn gevent

config file for bepasty -- ``/home/bepasty/bepasty.conf``:

Copy ``src/bepasty/config.py`` to ``/home/bepasty/bepasty.conf`` first,
remove the ``class Config`` and remove all indents in the file.
The comments can be removed too, if you feel the need to.
At last modify these two configs variables:

::

  STORAGE = 'filesystem'
  STORAGE_FILESYSTEM_DIRECTORY = '/home/bepasty/storage/'


add this content to ``/home/bepasty/bin/gunicorn_bepasty``:

::

  #!/bin/bash

  NAME="bepasty"
  HOME=/home/bepasty
  SOCKFILE=$HOME/gunicorn.sock  # we will communicate using this unix socket
  PIDFILE=$HOME/gunicorn.pid
  NUM_WORKERS=3                 # how many worker processes should Gunicorn spawn
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

A nginx configuration i.e. in ``/etc/nginx/conf.d/bepasty.conf``:

::

  upstream pasty_server {
    server unix:/home/bepasty/gunicorn.sock fail_timeout=0;
  }

  server {
    listen 80;
    #listen [::]:80; #uncomment this if your server supports IPv6
    server_name paste.example.org;  # <-- add your domainname here

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
