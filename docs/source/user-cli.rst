==================================
Using Bepasty with non-web clients
==================================

pastebinit
==========

pastebinit is a popular pastebin client (included in Debian, Ubuntu and maybe elsewhere) that can be configured to work with Bepasty:


Configuration
-------------

~/.pastebinit.xml::

    <pastebinit>
        <pastebin>https://bepasty.example.org</pastebin>
        <format></format>
    </pastebinit>

Notes:

* We set an empty default format so pastebinit will transmit this (and not its
  internal format default, which is "text" and completely useless for us as it
  is not a valid content type).

~/.pastebin.d/bepasty.conf::

    [pastebin]
    basename = bepasty.example.org
    regexp = https://bepasty.example.org

    [format]
    content = text
    title = filename
    format = contenttype
    page = page
    password = token

    [defaults]
    page = +upload


Usage
-----

Simplest::

    echo "test" | pastebinit

More advanced::

    # give title (filename), password, input file
    pastebinit -t example.py -p yourpassword -i example.py

    # read from stdin, give title (filename), give format (contenttype)
    cat README | pastebinit -t README -f text/plain

Notes:

* We use -t ("title") to transmit the desired filename (we do not have a
  "title", but the filename that is used for downloading the pastebin is
  prominently displayed above the content, so it can be considered a title as well).
* Bepasty guesses the content type from the filename given with -t. If you
  do not give a filename there or the content type is not guessable from it,
  you may need to give -f also (e.g., -f text/plain).
* If you give the content type, but not the filename, Bepasty will make up
  a filename.
* You need to use -p if the Bepasty instance you use requires you to log in
  before you can create pastebins.


curl
====

You can also use plain `curl <https://curl.se/>`_ to upload to and download from bepasty.

Upload a file and print the URL of the new item::

    curl -F token=yourpassword -F 'file=@example.txt' \
         -o /dev/null -w '%{redirect_url}\n' https://bepasty.example.org/+upload

Upload text from stdin, giving the filename and content type::

    echo "some text" | curl -F token=yourpassword -F 'text=<-' \
         -F filename=notes.txt -F contenttype=text/plain \
         -o /dev/null -w '%{redirect_url}\n' https://bepasty.example.org/+upload

Give the content type of a file and a lifetime (the default is 1 month, see
``DEFAULT_MAXLIFE_UNIT`` in the server configuration; units are minutes,
hours, days, weeks, months, years or forever)::

    curl -F token=yourpassword -F 'file=@example.txt;type=text/plain' \
         -F maxlife-value=1 -F maxlife-unit=days \
         -o /dev/null -w '%{redirect_url}\n' https://bepasty.example.org/+upload

Download an item (saved under its original filename, curl refuses to
overwrite an existing file)::

    curl -u :yourpassword -O -J https://bepasty.example.org/ITEMNAME/+download

Notes:

* ``-F token=yourpassword`` is only needed if the bepasty instance requires you
  to log in before you can create or read items. For uploads, prefer it over
  ``-u :yourpassword`` (HTTP basic auth, user name is ignored): with ``-u``,
  curl puts your password into the URL printed by ``%{redirect_url}``, so you
  could accidentally share it together with the URL.
* The upload is done in a single request, so the file must not exceed
  ``MAX_ALLOWED_FILE_SIZE`` in the bepasty configuration and must fit into the
  maximum request body size of a reverse proxy in front of bepasty (e.g.
  ``client_max_body_size`` for Nginx), otherwise you get a "413 Request Entity
  Too Large" error.
* For bigger files or more control, see the REST API (it supports chunked
  uploads) and the bepasty-client-cli project.
