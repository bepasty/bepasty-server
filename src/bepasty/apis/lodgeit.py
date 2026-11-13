import time
from io import BytesIO

from flask import request
from flask.views import MethodView
from pygments.lexers import get_all_lexers
from werkzeug.exceptions import Forbidden

from ..constants import FOREVER
from ..utils.date_funcs import limit_maxlife
from ..utils.http import redirect_next
from ..utils.permissions import CREATE, may
from ..utils.upload import create_item


class LodgeitUpload(MethodView):
    """
    LodgeIt paste form.
    """
    # Most functionality LodgeIt supports comes directly from Pygments;
    # for all other cases, we fall back to text/plain.
    TRANS = {}
    for lexer in get_all_lexers():
        # (name, aliases, filetypes, mimetypes)
        # e.g. ('Diff', ('diff',), ('*.diff', '*.patch'), ('text/x-diff', 'text/x-patch'))
        if len(lexer[1]) == 0:
            continue
        name = lexer[1][0]
        cts = lexer[3]
        # Find a content type, preferably one with text/*
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
        # t is already Unicode, but we want UTF-8 for storage
        t = t.encode('utf-8')
        size = len(t)
        f = BytesIO(t)
        maxtime = limit_maxlife(FOREVER)  # lodgeit clients can't choose, keep as long as allowed
        maxlife_timestamp = int(time.time()) + maxtime if maxtime > 0 else maxtime
        name = create_item(f, filename, size, content_type, content_type_hint,
                           maxlife_stamp=maxlife_timestamp)
        return redirect_next('bepasty.display', name=name)
