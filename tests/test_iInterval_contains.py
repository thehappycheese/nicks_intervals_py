import pytest

from nicks_intervals.Bound import Bound, PART_OF_LEFT, PART_OF_RIGHT
from nicks_intervals.Interval import Interval
import nicks_intervals._operators as ops


def test_iInterval_contains_value():
	a = Interval.closed(1.0, 2.0)
	assert a.contains_value(0.9) is False
	assert a.contains_value(1.0) is True
	assert a.contains_value(1.5) is True
	assert a.contains_value(2.0) is True
	assert a.contains_value(2.1) is False
	
	a = Interval.open(1.0, 2.0)
	assert a.contains_value(0.0) is False
	assert a.contains_value(1.0) is False
	assert a.contains_value(1.000001) is True
	assert a.contains_value(1.999999) is True
	assert a.contains_value(2.0) is False
	assert a.contains_value(3.0) is False


def test_iInterval_contains_bound():
	
	# See ponderings.md in /docs for graphical representation of Truth Table
	
	interval_open = Interval.open(1, 2)
	interval_closed = Interval.closed(1, 2)
	
	lower_left	= Bound(1, PART_OF_LEFT)
	lower_right	= Bound(1, PART_OF_RIGHT)
	
	upper_left	= Bound(2, PART_OF_LEFT)
	upper_right	= Bound(2, PART_OF_RIGHT)
	
	# Open Upper Contains
	assert ops.contains_upper_bound_atomic(interval_open, upper_right) is True
	assert ops.contains_upper_bound_atomic(interval_open, upper_left) is False
	assert ops.contains_lower_bound_atomic(interval_open, upper_left) is False
	assert ops.contains_lower_bound_atomic(interval_open, upper_right) is False
	
	# Open Lower Contains
	assert ops.contains_upper_bound_atomic(interval_open, lower_right) is False
	assert ops.contains_upper_bound_atomic(interval_open, lower_left) is False
	assert ops.contains_lower_bound_atomic(interval_open, lower_left) is True
	assert ops.contains_lower_bound_atomic(interval_open, lower_right) is False
	
	# Closed Upper Contains
	assert ops.contains_upper_bound_atomic(interval_closed, upper_right) is True
	assert ops.contains_upper_bound_atomic(interval_closed, upper_left) is True
	assert ops.contains_lower_bound_atomic(interval_closed, upper_left) is False
	assert ops.contains_lower_bound_atomic(interval_closed, upper_right) is True
	
	# Closed Lower Contains
	assert ops.contains_upper_bound_atomic(interval_closed, lower_right) is False
	assert ops.contains_upper_bound_atomic(interval_closed, lower_left) is True
	assert ops.contains_lower_bound_atomic(interval_closed, lower_left) is True
	assert ops.contains_lower_bound_atomic(interval_closed, lower_right) is True


def test_iInterval_contains_interval():
	
	a = 40.0
	b = 60.0
	
	def both_bounds_closed(mod):
		# both bounds closed
		assert Interval.closed(a, b).contains_interval(Interval.closed(a, b)) is True
		assert Interval.closed(a, b).contains_interval(Interval.closed(a, b - mod)) is True
		assert Interval.closed(a, b).contains_interval(Interval.closed(a + mod, b)) is True
		assert Interval.closed(a, b).contains_interval(Interval.closed(a + mod, b - mod)) is True
		assert Interval.closed(a, b).contains_interval(Interval.closed(a - mod, b)) is False
		assert Interval.closed(a, b).contains_interval(Interval.closed(a, b + mod)) is False
		assert Interval.closed(a, b).contains_interval(Interval.closed(a - mod, b + mod)) is False
		assert Interval.closed(a, b).contains_interval(Interval.closed(a + mod, b + mod)) is False
		assert Interval.closed(a, b).contains_interval(Interval.closed(a - mod, b - mod)) is False
		assert Interval.closed(a, b).contains_interval(Interval.closed(a - 10, a)) is False
		assert Interval.closed(a, b).contains_interval(Interval.closed(a - 10, a - mod)) is False
		assert Interval.closed(a, b).contains_interval(Interval.closed(b, b + 10)) is False
		assert Interval.closed(a, b).contains_interval(Interval.closed(b + mod, b + 10)) is False
	
	both_bounds_closed(1.0)
	both_bounds_closed(1.0e-7)
	with pytest.raises(AssertionError):
		both_bounds_closed(1.0e-8)
		
	# we will just do some sample cases with open closed ends #TODO: can we make this an exhaustive test?
	assert Interval.open(1, 2).contains_interval(Interval.open(1, 2)) is True
	assert Interval.open_closed(1, 2).contains_interval(Interval.open_closed(1, 2)) is True
	assert Interval.closed_open(1, 2).contains_interval(Interval.closed_open(1, 2)) is True
	
	assert Interval.open(1, 2).contains_interval(Interval.closed(1, 1.5)) is False
	assert Interval.open(1, 2).contains_interval(Interval.closed(1.5, 2)) is False
	
	assert Interval.closed(1, 2).contains_interval(Interval.open(1, 1.5)) is True
	assert Interval.closed(1, 2).contains_interval(Interval.open(1.5, 2)) is True
