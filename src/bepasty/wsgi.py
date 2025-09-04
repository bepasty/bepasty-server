#!/usr/bin/python
"""WSGI entry point for running the Bepasty application."""

from .app import create_app

application = create_app()

if __name__ == '__main__':
    application.run(debug=True)
