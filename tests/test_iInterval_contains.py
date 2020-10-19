import os
import sys
import pytest

#print(os.path.join(os.getcwd(), "\\"))
#sys.path.insert(len(sys.path), os.path.join(os.getcwd(), "\\"))

from NicksIntervals.iInterval import iInterval
from NicksIntervals.iBound import iBound, PART_OF_LEFT, PART_OF_RIGHT





def test_iInterval_contains_value():
	a = iInterval.closed(1.0, 2.0)
	assert a.contains_value(0.9) is False
	assert a.contains_value(1.0) is True
	assert a.contains_value(1.5) is True
	assert a.contains_value(2.0) is True
	assert a.contains_value(2.1) is False
	
	a = iInterval.open(1.0, 2.0)
	assert a.contains_value(0.0) is False
	assert a.contains_value(1.0) is False
	assert a.contains_value(1.000001) is True
	assert a.contains_value(1.999999) is True
	assert a.contains_value(2.0) is False
	assert a.contains_value(3.0) is False


def test_iInterval_contains_bound():
	
	# See ponderings.md in /docs for graphical representation of Truth Table
	
	interval_open = iInterval.open(1, 2)
	interval_closed = iInterval.closed(1, 2)
	
	lower_left	= iBound(1, PART_OF_LEFT)
	lower_right	= iBound(1, PART_OF_RIGHT)
	
	upper_left	= iBound(2, PART_OF_LEFT)
	upper_right	= iBound(2, PART_OF_RIGHT)
	
	# Open Upper Contains
	assert interval_open.contains_upper_bound(upper_right) is True
	assert interval_open.contains_upper_bound(upper_left) is False
	assert interval_open.contains_lower_bound(upper_left) is False
	assert interval_open.contains_lower_bound(upper_right) is False
	
	# Open Lower Contains
	assert interval_open.contains_upper_bound(lower_right) is False
	assert interval_open.contains_upper_bound(lower_left) is False
	assert interval_open.contains_lower_bound(lower_left) is True
	assert interval_open.contains_lower_bound(lower_right) is False
	
	# Closed Upper Contains
	assert interval_closed.contains_upper_bound(upper_right) is True
	assert interval_closed.contains_upper_bound(upper_left) is True
	assert interval_closed.contains_lower_bound(upper_left) is False
	assert interval_closed.contains_lower_bound(upper_right) is True
	
	# Closed Lower Contains
	assert interval_closed.contains_upper_bound(lower_right) is False
	assert interval_closed.contains_upper_bound(lower_left) is True
	assert interval_closed.contains_lower_bound(lower_left) is True
	assert interval_closed.contains_lower_bound(lower_right) is True


def test_iInterval_contains_interval():
	
	# TODO: test some edge cases with open and closed ends.
	
	a = 40.0
	b = 60.0
	
	def both_bounds_closed(mod):
		# both bounds closed
		assert iInterval.closed(a, b).contains_interval(iInterval.closed(a, b)) is True
		assert iInterval.closed(a, b).contains_interval(iInterval.closed(a, b - mod)) is True
		assert iInterval.closed(a, b).contains_interval(iInterval.closed(a + mod, b)) is True
		assert iInterval.closed(a, b).contains_interval(iInterval.closed(a + mod, b - mod)) is True
		assert iInterval.closed(a, b).contains_interval(iInterval.closed(a - mod, b)) is False
		assert iInterval.closed(a, b).contains_interval(iInterval.closed(a, b + mod)) is False
		assert iInterval.closed(a, b).contains_interval(iInterval.closed(a - mod, b + mod)) is False
		assert iInterval.closed(a, b).contains_interval(iInterval.closed(a + mod, b + mod)) is False
		assert iInterval.closed(a, b).contains_interval(iInterval.closed(a - mod, b - mod)) is False
		assert iInterval.closed(a, b).contains_interval(iInterval.closed(a - 10, a)) is False
		assert iInterval.closed(a, b).contains_interval(iInterval.closed(a - 10, a-mod)) is False
		assert iInterval.closed(a, b).contains_interval(iInterval.closed(b, b+10)) is False
		assert iInterval.closed(a, b).contains_interval(iInterval.closed(b+mod, b + 10)) is False
	
	both_bounds_closed(1.0)
	both_bounds_closed(1.0e-7)
	with pytest.raises(AssertionError):
		both_bounds_closed(1.0e-8)
