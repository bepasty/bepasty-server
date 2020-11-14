import time
from flask import current_app
from werkzeug.exceptions import BadRequest

from ..constants import FOREVER, TIMESTAMP_MAX_LIFE


def get_maxlife(data, underscore):
    unit_key = 'maxlife_unit' if underscore else 'maxlife-unit'
    unit_default = 'MONTHS'
    unit = data.get(unit_key, unit_default).upper()
    value_key = 'maxlife_value' if underscore else 'maxlife-value'
    value_default = '1'
    try:
        value = int(data.get(value_key, value_default))
    except (ValueError, TypeError):
        raise BadRequest(description='{} header is incorrect'.format(value_key))
    try:
        return time_unit_to_sec(value, unit)
    except KeyError:
        raise BadRequest(description='{} header is incorrect'.format(unit_key))


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
        'FOREVER': FOREVER,
    }
    secs = units[unit] * value if units[unit] > 0 else units[unit]
    return secs


def delete_if_lifetime_over(item, name):
    """
    :return: True if file was deleted
    """
    if 0 < item.meta[TIMESTAMP_MAX_LIFE] < time.time():
        try:
            current_app.storage.remove(name)
        except (OSError, IOError):
            pass
        return True
    return False
