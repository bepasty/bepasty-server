bepasty
=======

bepasty is like a pastebin for all kinds of files (text, image, audio, video,
documents, ..., binary).

The documentation is there:
http://bepasty-server.readthedocs.org/en/latest/

Features
--------

* Generic:

  - you can upload multiple files at once, simply by drag and drop
  - after upload, you get a unique link to a view of each file
  - on that view, we offer:

    + download link
    + upload time (UTC)
    + file name we stored at upload time
    + file type we detected at upload time
    + precise size we computed at upload time
    + SHA256 hash ("checksum")

  - if you uploaded multiple files, you can create a pastebin with the list
    of all these files - with a single click!

* Text files:

  - we highlight all text file types supported by pygments (a lot!)
  - we display line numbers
  - we link from line numbers to their anchors, so you can easily get a link
    to a specific line

* Image files:

  - we show the image (format support depends on browser)

* Audio and video files:

  - we show the html5 player for it (format support depends on browser)

* PDFs:

  - we support rendering PDFs in your browser (if your browser is able to)

* Storage: we use a storage backend api, currently we have backends for:

  - filesystem storage (just use a filesystem directory to store
    <uuid>.meta and <uuid>.data files)
  - ceph cluster storage (distributed & fault-tolerant - uses RADOS Block
    Devices via librbd and librados)

* Keeping some control:

  - flexible permissions: create, read, delete, admin
  - assign permissions to users of login secrets
  - assign default permissions to not-logged-in users
  - you can purge files from storage by age, inactivity, size, type, ...
