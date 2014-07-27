# Copyright: 2014 Thomas Waldmann <tw@waldmann-edv.de>
# License: BSD 2-clause, see LICENSE for details.

from StringIO import StringIO
import time

from flask import request
from flask.views import MethodView
from werkzeug.exceptions import Forbidden
from pygments.lexers import get_lexer_by_name, get_all_lexers

from . import blueprint
from werkzeug.urls import url_quote
from ..utils.date_funcs import FOREVER
from ..utils.permissions import *
from ..utils.http import redirect_next
from ..utils.name import ItemName
from ..utils.upload import Upload, create_item


class LodgeitUpload(MethodView):
    """
    lodgeit paste form
    """
    # most stuff lodgeit support comes directly from pygments
    # for all other stuff we fall back to text/plain.
    TRANS = {}
    for lexer in get_all_lexers():
        # (name, aliases, filetypes, mimetypes)
        # e.g. ('Diff', ('diff',), ('*.diff', '*.patch'), ('text/x-diff', 'text/x-patch'))
        name = lexer[1][0]
        cts = lexer[3]
        # find a content-type, preferably one with text/*
        for ct in cts:
            if ct.startswith("text/"):
                break
        else:
            if cts:
                ct = cts[0]
            else:
                ct = None
        if ct:
            TRANS[name] = ct

    def post(self):
        if not may(CREATE):
            raise Forbidden()
        lang = request.form.get('language')
        content_type = self.TRANS.get(lang)
        content_type_hint = 'text/plain'
        filename = None
        t = request.form['code']
        # t is already unicode, but we want utf-8 for storage
        t = t.encode('utf-8')
        size = len(t)
        f = StringIO(t)
        maxlife_timestamp = FOREVER
        name = create_item(f, filename, size, content_type, content_type_hint,
                           maxlife_stamp=maxlife_timestamp)
        return redirect_next('bepasty.display', name=name, _anchor=url_quote(filename))


blueprint.add_url_rule('/lodgeit/', view_func=LodgeitUpload.as_view('lodgeit'))
