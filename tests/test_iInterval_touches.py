import pytest

from nicks_intervals.Bound import Bound, PART_OF_LEFT, PART_OF_RIGHT
from nicks_intervals.Interval import Interval


def test_iInterval_touches():
	a = Interval.closed(1.0, 2.0)
	assert a.touches(Interval.open(0.0, 1.0)) is True
	assert a.touches(Interval.open(2.0, 3.0)) is True
	assert a.touches(Interval.closed(0.0, 1.0)) is False
	assert a.touches(Interval.closed(2.0, 3.0)) is False
	
	a = Interval.open(1.0, 2.0)
	assert a.touches(Interval.open(0.0, 1.0)) is False
	assert a.touches(Interval.open(2.0, 3.0)) is False
	assert a.touches(Interval.closed(0.0, 1.0)) is True
	assert a.touches(Interval.closed(2.0, 3.0)) is True

