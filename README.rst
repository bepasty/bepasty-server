bepasty
=======

bepasty is like a pastebin for all kinds of files (text, image, audio, video,
documents, ..., binary).

The documentation is there:
https://bepasty-server.readthedocs.org/en/latest/

Features
--------

* Generic:

  - you can upload multiple files at once, simply by drag and drop
  - after upload, you get a unique link to a view of each file
  - on that view, we show actions you can do with the file, metadata of the
    file and, if possible, we also render the file contents
  - if you uploaded multiple files, you can create a pastebin with the list
    of all these files - with a single click!
  - Set an expiration date for your files

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
  - currently there are no other storage implementations in master branch
    and releases. The "ceph cluster" storage implementation has issues and
    currently lives in branch "ceph-storage" until these issues are fixed.

* Keeping some control:

  - flexible permissions: create, read, delete, admin
  - assign permissions to users of login secrets
  - assign default permissions to not-logged-in users
  - you can purge files from storage by age, inactivity, size, type, ...
  - you can do consistency checks on the storage

Development
-----------

::

    # Clone the official bepasty-server (or your fork, if you want to send PULL requests)
    git clone https://github.com/bepasty/bepasty-server.git
    cd bepasty-server
    # Create a new virtualenv
    virtualenv ~/bepasty
    # Activate the virtualenv
    source ~/bepasty/bin/activate
    # This will use the current directory for the installed package
    # Very useful during development! It will also autoreload when files are changed
    pip install -e .
    # Run the bepasty-server in debug mode. The server is reachable in http://127.0.0.1:5000
    bepasty-server --debug

