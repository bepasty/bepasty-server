# Copyright: 2013 Bastian Blank <bastian@waldi.eu.org>
# License: BSD 2-clause, see LICENSE for details.

import errno

from flask import current_app, render_template, Markup, request, url_for
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
        except (OSError, IOError) as e:
            if e.errno == errno.ENOENT:
                return render_template('file_not_found.html'), 404

        with item as item:
            if not item.meta.get('unlocked'):
                error = 'File locked.'
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
            elif ct.startswith('image/'):
                src = url_for('bepasty.download', name=name)
                rendered_content = Markup(u'<img src="%s" width="800">' % src)
            elif ct.startswith('audio/'):
                src = url_for('bepasty.download', name=name)
                alt_msg = u'html5 audio element not supported by your browser.'
                rendered_content = Markup(u'<audio controls src="%s">%s</audio>' % (src, alt_msg))
            elif ct.startswith('video/'):
                src = url_for('bepasty.download', name=name)
                alt_msg = u'html5 video element not supported by your browser.'
                rendered_content = Markup(u'<video controls src="%s">%s</video>' % (src, alt_msg))
            else:
                rendered_content = u"Can't render this content type."
            return render_template('display.html', name=name, item=item,
                                   rendered_content=rendered_content)


blueprint.add_url_rule('/<itemname:name>', view_func=DisplayView.as_view('display'))
