Quickstart
==========

Installing bepasty
------------------

Currently bepasty isn't published on PyPi but you can install it from the git repository. Our master branch should be stable. *sigh*

::

    pip install -e git+https://github.com/bepasty/bepasty-server.git#egg=bepasty-server


Starting bepasty server
-----------------------

You can run the bepasty server after installation with following command.

::

    bepasty-server

The default config is to use the filesystem as storage location in /tmp.

.. warning::

    The default setting is that all files are unlocked. This means every user can upload and some other can download the file. If you host bepasty public you should set ``UPLOAD_UNLOCKED=False`` to avoid copyright issues.

You can use also another WSGI server like gunicorn.

::

    gunicorn bepasty.wsgi
