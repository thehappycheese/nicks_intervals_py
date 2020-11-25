import itertools

from NicksIntervals.iInterval import iInterval
from NicksIntervals.iMulti_iInterval import iMulti_iInterval


def test_eq_not():
	assert not any(a == b for a, b in itertools.combinations([
		iInterval.closed(0, 10),
		iInterval.open(0, 10),
		iInterval.closed_open(0, 10),
		iInterval.open_closed(0, 10)
	], 2))
	
	assert iInterval.inf_closed(10) != iInterval.inf_open(10)
	assert iInterval.closed_inf(10) != iInterval.open_inf(10)
	

def test_eq_multi():
	assert iMulti_iInterval([iInterval.closed(0, 10), iInterval.closed(0, 10)]) != iInterval.closed(0, 10)
	assert iInterval.closed(0, 10) != iMulti_iInterval([iInterval.closed(0, 10), iInterval.closed(0, 10)])
	assert iMulti_iInterval([iInterval.closed(0, 10), iInterval.closed(0, 10)]) == iMulti_iInterval([iInterval.closed(0, 10), iInterval.closed(0, 10)])