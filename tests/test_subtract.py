
from NicksIntervals.Interval import Interval
from NicksIntervals.Multi_Interval import Multi_Interval


def test_subtract():
	a = Interval.closed(0, 10)
	b = Interval.closed(5, 15)
	
	# test one bound overlapping subtraction
	assert a.subtract(b) == Interval.closed_open(0, 5)
	assert b.subtract(a) == Interval.open_closed(10, 15)
	assert a.subtract(a) == Interval.empty()
	assert b.subtract(b) == Interval.empty()
	
	# test disjoint subtraction
	c = Interval.closed(20, 25)
	assert c.subtract(a) == c
	assert a.subtract(c) == a
	
	# test complex subtraction produces multi interval.
	d = Interval.closed(2, 8)
	a_sub_d = Multi_Interval([Interval.closed_open(0, 2), Interval.open_closed(8, 10)])
	assert a.subtract(d) == a_sub_d
	assert d.subtract(a) == Interval.empty()
	# test re-subtraction produces no result.
	assert a_sub_d.subtract(d) == a_sub_d
	
	# test empty interval has no effect
	assert Interval.empty().subtract(a) == Interval.empty()
	assert a.subtract(Interval.empty()) == a
	
	# test infinite subtraction
	assert a.subtract(Interval.inf()) == Interval.empty()
	assert a_sub_d.subtract(Interval.inf()) == Interval.empty()
	
	# test subtraction from infinite
	assert Interval.inf().subtract(a) == Multi_Interval([Interval.inf_open(0), Interval.open_inf(10)])


def test_subtract_multi_interval():
	# test subtraction from multi interval preserves structure
	assert Multi_Interval([Interval.closed(0, 20), Interval.closed(0, 20), Interval.closed(0, 10)]).subtract(Interval.closed(10, 20)) == [Interval.closed_open(0, 10), Interval.closed_open(0, 10), Interval.closed_open(0, 10)]

def torture_test_subtract():
	inf = Interval.inf()
	ints = [Interval.open(a, a + 0.5) for a in range(10000)]
	ints_comp = [Interval.inf_closed(0), *[Interval.closed(a + 0.5, a + 1) for a in range(9999)], Interval.closed_inf(9999.5)]
	assert inf.subtract(ints) == ints_comp
