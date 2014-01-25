# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

import errno

from flask import current_app, render_template, Markup, request
from flask.views import MethodView
from werkzeug.exceptions import NotFound
from pygments import highlight
from pygments.lexers import get_lexer_for_mimetype
from pygments.formatters import HtmlFormatter


from ..utils.name import ItemName
from . import blueprint


class DisplayView(MethodView):
    def get(self, name):
        try:
            item = current_app.storage.open(name)
        except OSError as e:
            if e.errno == errno.ENOENT:
                raise NotFound()
            raise

        with item as item:
            if not item.meta.get('unlocked'):
                error = 'File Locked.'
            elif not item.meta.get('complete'):
                error = 'Upload incomplete. Try again later.'
            else:
                error = None
            if error:
                return render_template('display_error.html', name=name, item=item, error=error), 409
            ct = item.meta['type']
            if ct.startswith('text/'):
                code = item.data.read(item.data.size, 0)
                code = code.decode('utf-8')  # TODO we don't have the coding in metadata
                lexer = get_lexer_for_mimetype(ct)
                formatter = HtmlFormatter(linenos='table', lineanchors="L", anchorlinenos=True)
                rendered_content = Markup(highlight(code, lexer, formatter))
            else:
                rendered_content = u"Can't render non-text content types."
            return render_template('display.html', name=name, item=item,
                                   rendered_content=rendered_content)


blueprint.add_url_rule('/<itemname:name>', view_func=DisplayView.as_view('display'))
