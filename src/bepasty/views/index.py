from flask import render_template

from pygments.lexers import get_all_lexers


def index():
    contenttypes = []
    for lexer_info in get_all_lexers():
        contenttypes.extend(lexer_info[3])
    return render_template('index.html', contenttypes=contenttypes)
