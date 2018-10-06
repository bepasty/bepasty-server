import pytest

from bepasty.constants import FOREVER
from bepasty.utils.date_funcs import time_unit_to_sec


@pytest.mark.parametrize('unit,expectation', [
    ('MINUTES', 60),
    ('HOURS', 60 * 60),
    ('DAYS', 60 * 60 * 24),
    ('WEEKS', 60 * 60 * 24 * 7),
    ('MONTHS', 60 * 60 * 24 * 30),
    ('YEARS', 60 * 60 * 24 * 365),
    ('FOREVER', FOREVER),
])
def test_unit_to_secs(unit, expectation):
    assert time_unit_to_sec(1, unit) == expectation
