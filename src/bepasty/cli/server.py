"""
bepasty-server commandline interface
"""

from __future__ import print_function
import argparse

from ..app import create_app


def main():
    argparser = argparse.ArgumentParser(prog='bepasty-server')
    argparser.add_argument('--host', help='Host to listen on')
    argparser.add_argument('--port', type=int, help='Port to listen on')
    argparser.add_argument('--debug', help='Activate debug mode', action='store_true')

    args = argparser.parse_args()
    app = create_app()
    print(" * Starting bepasty server...")
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()
