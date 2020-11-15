import errno
import time

from flask import current_app, render_template, Markup, url_for, request
from flask.views import MethodView
from werkzeug.exceptions import NotFound, Forbidden
from pygments import highlight
from pygments.lexers import get_lexer_for_mimetype
from pygments.util import ClassNotFound as NoPygmentsLexer

from ..constants import COMPLETE, FILENAME, LOCKED, SIZE, TIMESTAMP_DOWNLOAD, TYPE
from ..utils.date_funcs import delete_if_lifetime_over
from ..utils.formatters import CustomHtmlFormatter
from ..utils.permissions import ADMIN, READ, may

from .index import contenttypes_list
from .filelist import file_infos


def rendering_allowed(item_type, item_size, use_pygments, complete):
    """
    check if rendering is allowed, checks for:

    * whether the item is completely uploaded
    * whether the size is within the configured limits for the content-type
    """
    if not complete:
        return False
    if use_pygments:
        # if we use pygments, special restrictions apply
        item_type = 'HIGHLIGHT_TYPES'
    # create a tuple list [(content_type_prefix, max_size), ...] with long prefixes first
    ct_size = sorted(current_app.config['MAX_RENDER_SIZE'].items(), key=lambda e: len(e[0]), reverse=True)
    for ct, size in ct_size:
        if item_type.startswith(ct):
            return item_size <= size
    # there should be one entry with ct == '', so we should never get here:
    return False


class DisplayView(MethodView):
    def get(self, name):
        if not may(READ):
            raise Forbidden()
        try:
            item = current_app.storage.openwrite(name)
        except (OSError, IOError) as e:
            if e.errno == errno.ENOENT:
                raise NotFound()
            raise

        with item as item:
            complete = item.meta[COMPLETE]
            if not complete and not may(ADMIN):
                error = 'Upload incomplete. Try again later.'
                return render_template('error.html', heading=item.meta[FILENAME], body=error), 409

            if item.meta[LOCKED] and not may(ADMIN):
                raise Forbidden()

            if delete_if_lifetime_over(item, name):
                raise NotFound()

            def read_data(item):
                # reading the item for rendering is registered like a download
                data = item.data.read(item.data.size, 0)
                item.meta[TIMESTAMP_DOWNLOAD] = int(time.time())
                return data

            size = item.meta[SIZE]
            ct = item.meta[TYPE]
            try:
                get_lexer_for_mimetype(ct)
                use_pygments = True
                ct_pygments = ct
            except NoPygmentsLexer:
                if ct.startswith('text/'):
                    # seems like we found a text type not supported by pygments
                    # use text/plain so we get a display with line numbers
                    use_pygments = True
                    ct_pygments = 'text/plain'
                else:
                    use_pygments = False

            if rendering_allowed(ct, size, use_pygments, complete):
                if ct.startswith('text/x-bepasty-'):
                    # special bepasty items - must be first, don't feed to pygments
                    if ct == 'text/x-bepasty-list':
                        names = read_data(item).decode('utf-8').splitlines()
                        files = sorted(file_infos(names), key=lambda f: f[FILENAME])
                        rendered_content = Markup(render_template('filelist_tableonly.html', files=files))
                    elif ct == 'text/x-bepasty-redirect':
                        url = read_data(item).decode('utf-8')
                        delay = request.args.get('delay', '3')
                        return render_template('redirect.html', url=url, delay=delay)
                    else:
                        rendered_content = u"Can't render this content type."
                elif ct.startswith('image/'):
                    src = url_for('bepasty.download', name=name)
                    rendered_content = Markup(u'<img src="%s" alt="the image" width="800">' % src)
                elif ct.startswith('audio/'):
                    src = url_for('bepasty.download', name=name)
                    alt_msg = u'html5 audio element not supported by your browser.'
                    rendered_content = Markup(u'<audio controls src="%s">%s</audio>' % (src, alt_msg))
                elif ct.startswith('video/'):
                    src = url_for('bepasty.download', name=name)
                    alt_msg = u'html5 video element not supported by your browser.'
                    rendered_content = Markup(u'<video controls src="%s">%s</video>' % (src, alt_msg))
                elif ct in ['application/pdf', 'application/x-pdf', ]:
                    src = url_for('bepasty.inline', name=name)
                    link_txt = u'Click to see PDF'
                    rendered_content = Markup(u'<a href="%s">%s</a>' % (src, link_txt))
                elif ct == 'application/x-asciinema-recording':
                    src = url_for('bepasty.download', name=name)
                    rendered_content = Markup(u'<asciinema-player src="%s" title="%s" theme="%s" autoplay>' %
                                              (src, item.meta[FILENAME],
                                               current_app.config.get('ASCIINEMA_THEME', 'asciinema')))
                elif use_pygments:
                    text = read_data(item)
                    # TODO we don't have the coding in metadata
                    try:
                        text = text.decode('utf-8')
                    except UnicodeDecodeError:
                        # well, it is not utf-8 or ascii, so we can only guess...
                        text = text.decode('iso-8859-1')
                    lexer = get_lexer_for_mimetype(ct_pygments)
                    formatter = CustomHtmlFormatter(linenos='table', lineanchors="L",
                                                    lineparagraphs="L", anchorlinenos=True)
                    rendered_content = Markup(highlight(text, lexer, formatter))
                else:
                    rendered_content = u"Can't render this content type."
            else:
                if not complete:
                    rendered_content = u"Rendering not allowed (not complete). Is it still being uploaded?"
                else:
                    rendered_content = u"Rendering not allowed (too big?). Try download"

            return render_template('display.html', name=name, item=item,
                                   rendered_content=rendered_content,
                                   contenttypes=contenttypes_list())
