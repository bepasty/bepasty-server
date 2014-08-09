# Copyright: 2014 Valentin Pratz <vp.pratz@yahoo.de>
# License: BSD 2-clause, see LICENSE for details.

import time
from flask import current_app

FOREVER = -1


def time_unit_to_sec(value, unit):
    """
    Converts a numeric value and with a string time unit unit to a time in seconds

    :param value: int
    :param unit: str in ['MINUTES', 'HOURS', 'DAYS', 'WEEKS', 'MONTHS', 'YEARS', 'FOREVER']
    :return: time in seconds
    """
    units = {
        'MINUTES': 60,
        'HOURS': 60 * 60,
        'DAYS': 60 * 60 * 24,
        'WEEKS': 60 * 60 * 24 * 7,
        'MONTHS': 60 * 60 * 24 * 30,
        'YEARS': 60 * 60 * 24 * 365,
        'FOREVER': -1
    }
    secs = units[unit] * value if units[unit] > 0 else units[unit]
    return secs


def delete_if_lifetime_over(item, name):
    """
    :return: True if file was deleted
    """
    if 0 < item.meta['timestamp-max-life'] < time.time():
        try:
            current_app.storage.remove(name)
        except (OSError, IOError) as e:
            pass
        return True
    return False
