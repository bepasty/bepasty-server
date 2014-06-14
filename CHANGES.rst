ChangeLog
=========

Release <TBD>
-------------

New features:

* simple login/logout for uploaders - see TOKENS in config.py.
* support inline viewing of PDFs
* support Python 2.6
* after upload, show file url list in an easy to copy format
* file uploads can be aborted (partially uploaded file will get deleted)
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

* for chunked upload, a wrong hash was computed. Now it stores an empty hash as
  computing the correct hash is not possible with Python's hashlib api.
  The empty hashes can get fixed later by the consistency cli command.
* misc. cosmetic UI fixes
* add project docs


Release 0.0.1
-------------

* first pypi release. release early, release often! :)
