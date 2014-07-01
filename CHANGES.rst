ChangeLog
=========

Release 0.1.0
-------------

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


Release 0.0.1
-------------

* first pypi release. release early, release often! :)
