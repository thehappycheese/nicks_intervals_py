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


def test_iInterval_contains_lower_bound():
	# Touching inside cases:
	assert iInterval(iBound(1, False), iBound(2)).contains_lower_bound(iBound(1, False)) is True  # ?? amounts to 'contains nothing'... but is true since other bound is not inclusive
	assert iInterval(iBound(1, False), iBound(2)).contains_lower_bound(iBound(1, True)) is False
	assert iInterval(iBound(1, True), iBound(2)).contains_lower_bound(iBound(1, False)) is True
	assert iInterval(iBound(1, True), iBound(2)).contains_lower_bound(iBound(1, True)) is True
	
	# Touching outside cases:
	assert iInterval(iBound(1), iBound(2, False)).contains_lower_bound(iBound(2, False)) is False
	assert iInterval(iBound(1), iBound(2, False)).contains_lower_bound(iBound(2, True)) is False
	assert iInterval(iBound(1), iBound(2, True)).contains_lower_bound(iBound(2, False)) is False
	assert iInterval(iBound(1), iBound(2, True)).contains_lower_bound(iBound(2, True)) is True


def test_iInterval_contains_upper_bound():
	# Touching inside cases:
	assert iInterval(iBound(1), iBound(2, False)).contains_upper_bound(iBound(2, False)) is True  # ?? amounts to 'contains nothing'... but is true since other bound is not inclusive
	assert iInterval(iBound(1), iBound(2, False)).contains_upper_bound(iBound(2, True)) is False
	assert iInterval(iBound(1), iBound(2, True)).contains_upper_bound(iBound(2, False)) is True
	assert iInterval(iBound(1), iBound(2, True)).contains_upper_bound(iBound(2, True)) is True
	
	# Touching outside cases:
	assert iInterval(iBound(1, False), iBound(2)).contains_upper_bound(iBound(1, False)) is False
	assert iInterval(iBound(1, False), iBound(2)).contains_upper_bound(iBound(1, True)) is False
	assert iInterval(iBound(1, True), iBound(2)).contains_upper_bound(iBound(1, False)) is False
	assert iInterval(iBound(1, True), iBound(2)).contains_upper_bound(iBound(1, True)) is True

def test_iInterval_contains_interval():
	a = 40.0
	b = 60.0
	
	def both_bounds_closed(mod):
		# both bounds closed
		assert iInterval(a, b).contains_interval(iInterval(a, b)) is True
		assert iInterval(a, b).contains_interval(iInterval(a, b - mod)) is True
		assert iInterval(a, b).contains_interval(iInterval(a + mod, b)) is True
		assert iInterval(a, b).contains_interval(iInterval(a + mod, b - mod)) is True
		
		assert iInterval(a, b).contains_interval(iInterval(a - mod, b)) is False
		assert iInterval(a, b).contains_interval(iInterval(a, b + mod)) is False
		assert iInterval(a, b).contains_interval(iInterval(a - mod, b + mod)) is False
		
		assert iInterval(a, b).contains_interval(iInterval(a + mod, b + mod)) is False
		assert iInterval(a, b).contains_interval(iInterval(a - mod, b - mod)) is False
		
		assert iInterval(a, b).contains_interval(iInterval(a - 10, a)) is False
		assert iInterval(a, b).contains_interval(iInterval(a - 10, a-mod)) is False
		assert iInterval(a, b).contains_interval(iInterval(b, b+10)) is False
		assert iInterval(a, b).contains_interval(iInterval(b+mod, b + 10)) is False
	
	both_bounds_closed(1.0)
	both_bounds_closed(1.0e-7)
	with pytest.raises(AssertionError):
		both_bounds_closed(1.0e-8)
