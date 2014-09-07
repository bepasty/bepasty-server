from pygments.formatters.html import HtmlFormatter


class CustomHtmlFormatter(HtmlFormatter):
    """Custom HTML formatter. Adds an option to wrap lines into HTML <p> tags."""
    def __init__(self, **options):
        super(CustomHtmlFormatter, self).__init__(**options)
        self.lineparagraphs = options.get('lineparagraphs', '')

    def _wrap_lineparagraphs(self, inner):
        """Wrap lines into <p> tags

        :param inner: iterator of tuples of format (code, text)
        :return: iterator of tuples containing updated wrapped lines
        """
        s = self.lineparagraphs
        i = self.linenostart - 1
        for t, line in inner:
            if t:
                i += 1
                yield 1, '<p id="%s-%d">%s</p>' % (s, i, line)
            else:
                yield 0, line

    def format_unencoded(self, tokensource, outfile):
        """Format by wrapping pieces of text according to the user's options

        :param tokensource: iterator of tuples of format (code, text)
        :param outfile: output file handler
        """
        source = self._format_lines(tokensource)
        if self.hl_lines:
            source = self._highlight_lines(source)
        if not self.nowrap:
            if self.linenos == 2:
                source = self._wrap_inlinelinenos(source)
            if self.lineanchors:
                source = self._wrap_lineanchors(source)
            if self.linespans:
                source = self._wrap_linespans(source)
            if self.lineparagraphs:
                source = self._wrap_lineparagraphs(source)
            source = self.wrap(source, outfile)
            if self.linenos == 1:
                source = self._wrap_tablelinenos(source)
            if self.full:
                source = self._wrap_full(source, outfile)

        for t, piece in source:
            outfile.write(piece)
