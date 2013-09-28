#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

from bepasty import create_app

app = create_app()
if __name__ == '__main__':
    app.run(debug=True)
