============================
The bepasty software Project
============================

History
=======

The initial version of the bepasty(-server) software was developed in 48h in the WSGI Wrestle 2013 contest by:

* `Bastian Blank <bastian@waldi.eu.org>`_
* `Christian Fischer <cfischer@nuspace.de>`_


Project site
============

Source code repository, issue tracker (bugs, ideas about enhancements, todo,
feedback, ...), link to documentation is all there:

https://github.com/bepasty/


Contributing
============

Feedback is welcome.

If you find some issue, have some idea or some patch, please submit them via the issue tracker.

Or even better: if you use git, fork our repo, make your changes and submit a pull request.

For small fixes, you can even just edit the files on github (github will then fork, change and submit a pull request
automatically).

Development
===========

::

    # Create a new virtualenv
    virtualenv bepasty-server-env
    # Activate the virtualenv
    source bepasty-server-env/bin/activate
    # Clone the official bepasty-server (or your fork, if you want to send PULL requests)
    git clone https://github.com/bepasty/bepasty-server.git
    cd bepasty-server
    # This will use the current directory for the installed package.
    # Very useful during development! It will also autoreload when files are changed
    pip install -e .
    # Run the bepasty-server in debug mode. The server is reachable in http://127.0.0.1:5000
    bepasty-server --debug

