ChangeLog
=========

Release 1.0.0 (2021-03-14)
--------------------------

Compatibility:

* require Python >= 3.5, drop Python 2.x support

Fixes:

* pygments compatibility fix, #258.
  don't crash on ``('JSONBareObject', (), (), ())``.

Other changes:

* move away from Travis-CI, use github workflow for CI


Release 0.6.0 (2020-11-14)
--------------------------

Compatibility:

* drop python 3.4 support, #195
* note: this will likely be the last bepasty release supporting
  Python 2.x (2.7) and 3.5 (both are not supported by Python
  development any more).

Fixes:

* fix bad types for b64(en|de)code, #200
* use simple links in list/display view instead of <form> tags
* security fix: if PERMISSIONS in config are changed, we invalidate old
  clientside cookies now.
* fix creating empty file in storage/*
* fix dealing with expired items
* fix item.meta.get() in ItemDownloadView(), must be called with an argument.
* fix typo in get_maxlife (MONTH => MONTHS).

New features:

* add support for asciinema recordings, #175
* show QR code with link to bepasty item, #176
* support text/x-bepasty-redirect for URL redirects:
  just paste the target URL and choose this as mimetype to create a
  redirect. you may use the delay=<seconds> url argument to adjust
  the delay, default is 3s.
* add "modify" operation to modify uploaded data (web UI and REST),
  this is controlled by "modify" permissions entry.
* add optional python-magic support for application/octet-stream.
  Disabled by default, you can enable via: USE_PYTHON_MAGIC = True
* REST api:

  - add delete/lock/unlock REST api
  - use json for error response of REST api
  - use application/json for upload REST api

Other changes:

* support / test on py38, py39, #223
* move development section from README to project docs, #192
* use twine to upload releases, qubes gpg support, #197
* add config for readthedocs, #191
* code: some cleanups, fix warnings, fix minor errors
* theme:

  - upgrade to use bootstrap 4
  - use font-awesome everywhere, remove font-glyphicon, #232
  - use xstatic package for local font delivery
  - sort permission icons
  - misc. cosmetic fixes
* robustness / consistency improvements:

  - handle bad Transaction-ID, bad Content-Length, bad Maxlife-{Value,Unit},
    bad Range/Content-Range header
  - add exception handler for REST api to get consistent behaviour.
* tests:

  - add test for APP_BASE_PATH (for our prefix middleware)
  - add screen shots test for UI
  - add REST api tests


Release 0.5.0 (2018-10-15)
--------------------------

Compatibility:

* drop support for python 2.6 and 3.3
* add support for python 3.5, 3.6 and 3.7
* thus, you now need python 2.7 or python >= 3.4
* changes in source code layout: package bepasty is below src/ now
* thus, you need to install bepasty now: pip install -e .
* changed maxlife default from FOREVER to 1 MONTH. this avoids creating an
  ever-growing pastebin. users can still give other value if they like.

Fixes:

* REST api: fix off-by-one error in range calculations, #124
* config: reduce default body size by a 8kiB safety margin, #155
* multiple abort buttons for multiple file uploads, #29
* progress bar fixes, #131
* fix display of "undefined", should be "never", #129
* abort button now works w/ multiple files, #111
* upload form: don't linebreak in numbers, #122
* +list: work around 0-byte .meta files breaking the view, #147

New features:

* run bepasty at non-root URLs, see APP_BASE_PATH in the config.
* use icons instead of text for permissions (with hover-text)
* REST api: GET /apis/rest/items returns the list of all items

Other changes:

* re-style upload form
* add a favicon.ico (plus svg source)
* docs updates
* docs/config: clarify config updating, credentials/secrets, #151
* lots of cleanups for packaging, testing, source code
* upgrade xstatic package requirements, #171


Release 0.4.0 (2014-11-11)
--------------------------

New features:

* shorter, easy-to-read URLs / filenames (old uuid4 style URLs still supported,
  but not generated any more for new items)
* "list" permission separated from "admin" permission.

  - list: be able to list (discover) all pastebins
  - admin: be able to lock/unlock files, do actions even if upload is not
    completed or item is locked

  Make sure you update your PERMISSIONS configuration (you likely want to give
  "list" to the site administrator).

  By giving "list" (and/or "delete") permission to more users, you could
  operate your bepasty site in a rather public way (users seeing stuff from
  other users, maybe even being able to delete stuff they see).

Fixes:

* give configured limits to JS also, so stuff has not to be kept in sync manually, fixes #109
* highlighted text file views: set fixed width to line number column, fixes #108
* fixed crash for inline and download views when item was already deleted

Other changes:

* support Python 3.3+ additionally to 2.6+
* improved documentation, esp. about REST api
* improve sample configs


Release 0.3.0 (2014-08-22)
--------------------------

New features:

* support http basic auth header (it just reads the password from there, the
  user name is ignored). this is useful for scripting, e.g. you can do now:
  $ curl -F 'file=@somefile;type=text/plain' http://user:password@localhost:5000/+upload
* you can give the filename for the list items now
* do not use paste.txt as default filename, but <uuid>.txt or <uuid>.bin
  (this is less pretty, but avoids collisions if you download multiple files)
* allow uploading of multiple files via the fileselector of the browser
* display download (view) timestamp
* sorting of file lists
* use iso-8859-1 if decoding with utf-8 fails
* let admin directly delete locked files, without having to unlock first
* new bepasty-object cli command
* added REST api for bepasty-client-cli
* MAX_RENDER_SIZE can be used to set up maximum sizes for items of misc. types,
  so bepasty e.g. won't try to render a 1 GB text file with highlighting.
* offer a "max. lifetime" when creating a pastebin
* if you link to some specific text line, it will highlight that line now
* add filename to the pastebin url (as anchor)

Removed features:

* removed ceph-storage implementation due to bugs, missing features and general
  lack of maintenance. it is still in the repo in branch ceph-storage, waiting
  to be merged back after these issues have been fixed:
  https://github.com/bepasty/bepasty-server/issues/13
  https://github.com/bepasty/bepasty-server/issues/38

Fixes:

* security fix: when showing potentially dangerous text/* types, force the
  content-type to be text/plain and also turn the browser's sniffer off.
* security fix: prevent disclosure of locked item's metadata
* use POST for delete/lock actions
* application/x-pdf content-type items are offer for in-browser rendering, too
* fix typo in cli command bepasty-object set --incomplete (not: uncomplete)
* quite some UI / UX and other bug fixes
* filesystem storage: check if the configured directory is actually writeable

Other changes:

* using xstatic packages now for all 3rd party static files
* docs updated / enhanced


No release 0.2.0
----------------

We made quite quick progress due to many contributions from EuroPython 2014
sprint participants, so there was no 0.2.0 release and we directly jumped to
0.3.0.


Release 0.1.0 (2014-06-29)
--------------------------

New features:

* add a textarea so one now actually can paste (not just upload)
* simple login/logout and permissions system - see PERMISSIONS in config.py.
* add lock/unlock functionality to web UI (admin)
* add "List all items" on web UI (admin)
* add link to online documentation
* support inline viewing of PDFs
* support Python 2.6
* after upload of multiple files, offer creation of list item
* file uploads can be aborted (partially uploaded file will get deleted)
* store upload timestamp into metadata
* Compute hash of chunked uploads in a background thread directly after upload
  has finished.
* new migrate cli subcommand to upgrade stored metadata (see --help for details)
* new purge cli subcommand (see --help for details).
  you can use this to purge by age (since upload), inactivity (since last
  download), size or (mime)type.
  BEWARE: giving no criteria (like age, size, ...) means: purge all.
  Giving multiple criteria means they all must apply for files to get
  purged (AND - if you need OR, just run the command multiple times).
* new consistency cli subcommand (see --help for details).
  you can check consistency of hash/size in metadata against what you have
  in storage. Optionally, you can compute hashes (if an empty hash was stored)
  or fix the metadata with the computed hash/size values.
  also, you can remove files with inconsistent hash / size.

Fixes:

* for chunked upload, a wrong hash was computed. Fixed.
* misc. cosmetic UI fixes / misc. minor bug fixes
* add project docs
* use monospace font for textarea
* now correctly positions to linenumber anchors


Release 0.0.1 (2014-02-09)
--------------------------

* first pypi release. release early, release often! :)
