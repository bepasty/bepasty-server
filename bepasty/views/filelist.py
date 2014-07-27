# Copyright: 2014 Thomas Waldmann <tw@waldmann-edv.de>
# License: BSD 2-clause, see LICENSE for details.

import errno

from flask import current_app, render_template
from flask.views import MethodView
import time
from werkzeug.exceptions import Forbidden

from . import blueprint
from ..utils.permissions import *
from ..utils.date_funcs import delete_if_lifetime_over


def file_infos(names=None):
    """
    iterates over storage files metadata.
    note: we put the storage name into the metadata as 'id'

    :param names: None means "all items"
                  otherwise give a list of storage item names
    """
    storage = current_app.storage
    if names is None:
        names = list(storage)
    for name in names:
        try:
            with storage.open(name) as item:
                meta = dict(item.meta)
                if delete_if_lifetime_over(item, name):
                    continue
                meta['id'] = name
                yield meta
        except (OSError, IOError) as e:
            if e.errno != errno.ENOENT:
                raise


class FileListView(MethodView):
    def get(self):
        if not may(ADMIN):
            raise Forbidden()
        files = sorted(file_infos(), key=lambda f: f['timestamp-upload'], reverse=True)
        return render_template('filelist.html', files=files)


blueprint.add_url_rule('/+list', view_func=FileListView.as_view('filelist'))
