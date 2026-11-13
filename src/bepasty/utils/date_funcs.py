import time
from flask import current_app
from werkzeug.exceptions import BadRequest

from ..constants import FOREVER, TIMESTAMP_MAX_LIFE

UNITS = {
    'MINUTES': 60,
    'HOURS': 60 * 60,
    'DAYS': 60 * 60 * 24,
    'WEEKS': 60 * 60 * 24 * 7,
    'MONTHS': 60 * 60 * 24 * 30,
    'YEARS': 60 * 60 * 24 * 365,
    'FOREVER': FOREVER,
}


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
        secs = time_unit_to_sec(value, unit)
    except KeyError:
        raise BadRequest(description=f'{unit_key} header is incorrect')
    return limit_maxlife(secs)


def limit_maxlife(secs):
    """
    Limit a maximum lifetime to the configured MAX_LIFETIME.

    :param secs: max lifetime in seconds (or FOREVER)
    :return: max lifetime in seconds (or FOREVER), at most MAX_LIFETIME (if configured)
    """
    if secs <= 0:
        # FOREVER, but also 0 or negative values, which never expired either.
        secs = FOREVER
    max_lifetime = current_app.config.get('MAX_LIFETIME')
    if max_lifetime and (secs == FOREVER or secs > max_lifetime):
        secs = max_lifetime
    return secs


def allowed_maxlife_units():
    """
    Return the time units (lowercase) a user may choose for the maximum lifetime.

    If MAX_LIFETIME is configured, units of which even 1 exceeds it are not allowed,
    and neither is FOREVER.
    """
    max_lifetime = current_app.config.get('MAX_LIFETIME')
    return [unit.lower() for unit, secs in UNITS.items()
            if not max_lifetime or 0 < secs <= max_lifetime]


def time_unit_to_sec(value, unit):
    """
    Convert a numeric value with a string time unit to a time in seconds.

    :param value: int
    :param unit: str in ['MINUTES', 'HOURS', 'DAYS', 'WEEKS', 'MONTHS', 'YEARS', 'FOREVER']
    :return: time in seconds
    """
    secs = UNITS[unit] * value if UNITS[unit] > 0 else UNITS[unit]
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
