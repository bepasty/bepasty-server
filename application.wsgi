#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

from bepasty import create_app

app = create_app()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='BePasty Server')
    parser.add_argument('--host', help='Host to listen on')
    parser.add_argument('--port', type=int, help='Port to listen on')
    parser.add_argument('--debug', help='Activate debug mode',
                        action='store_true')
    args = parser.parse_args()

    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug
    )
