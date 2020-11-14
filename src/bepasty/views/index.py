from flask import render_template

from pygments.lexers import get_all_lexers


def contenttypes_list():
    contenttypes = [
        'text/x-bepasty-redirect',  # redirect / link shortener service
    ]
    for lexer_info in get_all_lexers():
        contenttypes.extend(lexer_info[3])
    return contenttypes


def index():
    return render_template('index.html', contenttypes=contenttypes_list())
