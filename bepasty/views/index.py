# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

from . import blueprint


@blueprint.route('/')
def index():
    from flask import render_template
    return render_template('index.html')
