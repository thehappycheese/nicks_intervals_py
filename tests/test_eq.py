import itertools

from nicks_intervals.Interval import Interval
from nicks_intervals.Multi_Interval import Multi_Interval


def test_eq_not():
	assert not any(a == b for a, b in itertools.combinations([
		Interval.closed(0, 10),
		Interval.open(0, 10),
		Interval.closed_open(0, 10),
		Interval.open_closed(0, 10)
	], 2))
	
	assert Interval.inf_closed(10) != Interval.inf_open(10)
	assert Interval.closed_inf(10) != Interval.open_inf(10)
	

def test_eq_multi():
	assert Multi_Interval([Interval.closed(0, 10), Interval.closed(0, 10)]) != Interval.closed(0, 10)
	assert Interval.closed(0, 10) != Multi_Interval([Interval.closed(0, 10), Interval.closed(0, 10)])
	assert Multi_Interval([Interval.closed(0, 10), Interval.closed(0, 10)]) == Multi_Interval([Interval.closed(0, 10), Interval.closed(0, 10)])