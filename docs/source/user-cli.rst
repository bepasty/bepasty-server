==================================
Using bepasty with non-web clients
==================================

pastebinit
==========

pastebinit is a popular pastebin client (included in debian, ubuntu and maybe
elsewhere) that can be configured to work with bepasty:


Configuration
-------------

~/.pastebinit.xml::

    <pastebinit>
        <pastebin>https://bepasty.example.org</pastebin>
        <format></format>
    </pastebinit>

Notes:

* we set an empty default format so pastebinit will transmit this (and not its
  internal format default [which is "text" and completely useless for us as it
  is not a valid contenttype])

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

* we use -t ("title") to transmit the desired filename (we do not have a
  "title", but the filename that is used for downloading the pastebin is
  prominently displayed above the content, so can be considered as title also).
* bepasty guesses the contenttype from the filename given with -t. if you
  do not give a filename there or the contenttype is not guessable from it,
  you may need to give -f also (e.g. -f text/plain).
* if you give the contenttype, but not the filename, bepasty will make up
  a filename.
* you need to use -p if the bepasty instance you use requires you to log in
  before you can create pastebins.
