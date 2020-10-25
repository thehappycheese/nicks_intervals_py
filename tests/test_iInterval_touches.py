import pytest

from NicksIntervals.iBound import iBound, PART_OF_LEFT, PART_OF_RIGHT
from NicksIntervals.iInterval import iInterval


def test_iInterval_touches():
	a = iInterval.closed(1.0, 2.0)
	assert a.touches(iInterval.open(0.0, 1.0)) is True
	assert a.touches(iInterval.open(2.0, 3.0)) is True
	assert a.touches(iInterval.closed(0.0, 1.0)) is False
	assert a.touches(iInterval.closed(2.0, 3.0)) is False
	
	a = iInterval.open(1.0, 2.0)
	assert a.touches(iInterval.open(0.0, 1.0)) is False
	assert a.touches(iInterval.open(2.0, 3.0)) is False
	assert a.touches(iInterval.closed(0.0, 1.0)) is True
	assert a.touches(iInterval.closed(2.0, 3.0)) is True

