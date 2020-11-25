
from NicksIntervals.iInterval import iInterval
from NicksIntervals.iMulti_iInterval import iMulti_iInterval


def test_subtract():
	a = iInterval.closed(0, 10)
	b = iInterval.closed(5, 15)
	
	# test one bound overlapping subtraction
	assert a.subtract(b) == iInterval.closed_open(0, 5)
	assert b.subtract(a) == iInterval.open_closed(10, 15)
	assert a.subtract(a) == iInterval.empty()
	assert b.subtract(b) == iInterval.empty()
	
	# test disjoint subtraction
	c = iInterval.closed(20, 25)
	assert c.subtract(a) == c
	assert a.subtract(c) == a
	
	# test complex subtraction produces multi interval.
	d = iInterval.closed(2, 8)
	a_sub_d = iMulti_iInterval([iInterval.closed_open(0, 2), iInterval.open_closed(8, 10)])
	assert a.subtract(d) == a_sub_d
	assert d.subtract(a) == iInterval.empty()
	# test re-subtraction produces no result.
	assert a_sub_d.subtract(d) == a_sub_d
	
	# test empty interval has no effect
	assert iInterval.empty().subtract(a) == iInterval.empty()
	assert a.subtract(iInterval.empty()) == a
	
	# test infinite subtraction
	assert a.subtract(iInterval.inf()) == iInterval.empty()
	assert a_sub_d.subtract(iInterval.inf()) == iInterval.empty()
	
	# test subtraction from infinite
	assert iInterval.inf().subtract(a) == iMulti_iInterval([iInterval.inf_open(0), iInterval.open_inf(10)])


def test_subtract_multi_interval():
	# test subtraction from multi interval preserves structure
	assert iMulti_iInterval([iInterval.closed(0, 20), iInterval.closed(0, 20), iInterval.closed(0, 10)]).subtract(iInterval.closed(10, 20)) == [iInterval.closed_open(0, 10), iInterval.closed_open(0, 10), iInterval.closed_open(0, 10)]

def torture_test_subtract():
	inf = iInterval.inf()
	ints = [iInterval.open(a, a+0.5) for a in range(10000)]
	ints_comp = [iInterval.inf_closed(0), *[iInterval.closed(a+0.5, a+1) for a in range(9999)], iInterval.closed_inf(9999.5)]
	assert inf.subtract(ints) == ints_comp
