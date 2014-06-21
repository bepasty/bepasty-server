# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

from pygments.lexers import get_all_lexers

from . import blueprint


@blueprint.route('/')
def index():
    from flask import render_template
    contenttypes = []
    for lexer_info in get_all_lexers():
        contenttypes.extend(lexer_info[3])
    return render_template('index.html',
                           contenttypes=contenttypes)
