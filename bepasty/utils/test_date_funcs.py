# Copyright: 2014 Valentin Pratz <vp.pratz@yahoo.de>
# License: BSD 2-clause, see LICENSE for details.

from ..utils.date_funcs import time_unit_to_sec, FOREVER


def test_unit_to_secs():
    cases = {
        'MINUTES': 60,
        'HOURS': 60 * 60,
        'DAYS': 60 * 60 * 24,
        'WEEKS': 60 * 60 * 24 * 7,
        'MONTHS': 60 * 60 * 24 * 30,
        'YEARS': 60 * 60 * 24 * 365,
        'FOREVER': FOREVER
    }
    for key, value in cases.items():
        yield compute_1_unit_to_sec, key, value


def compute_1_unit_to_sec(unit, expectation):
    assert time_unit_to_sec(1, unit) == expectation
