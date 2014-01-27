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
    + file name we stored at upload time
    + file type we detected at upload time
    + precise size we computed at upload time
    + SHA256 hash ("checksum") we computed at upload time

* Text files:

  - we highlight all text file types supported by pygments (a lot!)
  - we display line numbers
  - we link from line numbers to their anchors, so you can easily get a link
    to a specific line

* Image files:

  - we show the image (format support depends on browser)

* Audio and video files:

  - we show the html5 player for it (format support depends on browser)
