============================
The Bepasty Software Project
============================

History
=======

The initial version of the Bepasty (-server) software was developed in 48 hours during the WSGI Wrestle 2013 contest by:

* `Bastian Blank <bastian@waldi.eu.org>`_
* `Christian Fischer <cfischer@nuspace.de>`_


Project site
============

Source code repository, issue tracker (bugs, enhancement ideas, to-dos, feedback, …), and a link to the documentation are all there:

https://github.com/bepasty/


Contributing
============

Feedback is welcome.

If you find an issue, have an idea, or a patch, please submit it via the issue tracker.

Or, even better: if you use Git, fork our repo, make your changes, and submit a pull request.

For small fixes, you can even just edit the files on GitHub (GitHub will then fork, change, and submit a pull request
automatically).

Development
===========

::

    # Create a new virtualenv
    virtualenv bepasty-server-env
    # Activate the virtualenv
    source bepasty-server-env/bin/activate
    # Clone the official bepasty-server (or your fork, if you want to send pull requests)
    git clone https://github.com/bepasty/bepasty-server.git
    cd bepasty-server
    # This will use the current directory for the installed package.
    # Very useful during development! It will also auto-reload when files are changed.
    pip install -e .
    # Run the Bepasty server in debug mode. The server is reachable at http://127.0.0.1:5000
    bepasty-server --debug

