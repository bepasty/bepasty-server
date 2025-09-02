from flask import render_template

from pygments.lexers import get_all_lexers


def contenttypes_list():
    """
    Build a list of supported content types for the upload form.

    Includes bepasty’s redirect/link shortener type and all mimetypes
    advertised by Pygments lexers.
    """
    contenttypes = [
        'text/x-bepasty-redirect',  # redirect/link shortener service
    ]
    for lexer_info in get_all_lexers():
        # lexer_info format: (name, aliases, filetypes, mimetypes)
        contenttypes.extend(lexer_info[3])
    return contenttypes


def index():
    return render_template('index.html', contenttypes=contenttypes_list())
