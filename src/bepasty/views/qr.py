from flask import render_template, url_for
from flask.views import MethodView


class QRView(MethodView):
    """Render a QR code that links to the public display URL of an item."""
    def get(self, name):
        target = url_for('bepasty.display', name=name, _external=True)
        return render_template('qr.html', text=target)
