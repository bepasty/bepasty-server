import time
from flask import current_app
from werkzeug.exceptions import BadRequest

from ..constants import FOREVER, TIMESTAMP_MAX_LIFE


def get_maxlife(data, underscore):
    """
    Determine the maximum lifetime in seconds from request-like data.

    Reads either dashed or underscored keys depending on the 'underscore' flag.

    :param data: mapping containing the headers/fields
    :param underscore: bool; if True, use underscored keys, else dashed keys
    :return: max lifetime in seconds (or FOREVER)
    :raises BadRequest: if provided values are invalid
    """
    unit_key = 'maxlife_unit' if underscore else 'maxlife-unit'
    # Users can set DEFAULT_MAXLIFE_VALUE (int) and DEFAULT_MAXLIFE_UNIT (str).
    unit_default = current_app.config.get('DEFAULT_MAXLIFE_UNIT', 'MONTHS')
    unit = str(data.get(unit_key, unit_default)).upper()
    value_key = 'maxlife_value' if underscore else 'maxlife-value'
    value_default = str(current_app.config.get('DEFAULT_MAXLIFE_VALUE', 1))
    try:
        value = int(data.get(value_key, value_default))
    except (ValueError, TypeError):
        raise BadRequest(description=f'{value_key} header is incorrect')
    try:
        return time_unit_to_sec(value, unit)
    except KeyError:
        raise BadRequest(description=f'{unit_key} header is incorrect')


def time_unit_to_sec(value, unit):
    """
    Convert a numeric value with a string time unit to a time in seconds.

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
    Delete the file if its maximum lifetime has expired.

    :return: True if the file was deleted, otherwise False
    """
    if 0 < item.meta[TIMESTAMP_MAX_LIFE] < time.time():
        try:
            current_app.storage.remove(name)
        except OSError:
            pass
        return True
    return False
