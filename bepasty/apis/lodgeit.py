from io import BytesIO

from flask import request
from flask.views import MethodView
from pygments.lexers import get_all_lexers
from werkzeug.exceptions import Forbidden
from werkzeug.urls import url_quote

from ..constants import FOREVER
from ..utils.http import redirect_next
from ..utils.permissions import CREATE, may
from ..utils.upload import create_item


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
        if len(lexer[1]) == 0:
            continue
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
        f = BytesIO(t)
        maxlife_timestamp = FOREVER
        name = create_item(f, filename, size, content_type, content_type_hint,
                           maxlife_stamp=maxlife_timestamp)
        return redirect_next('bepasty.display', name=name, _anchor=url_quote(filename))
