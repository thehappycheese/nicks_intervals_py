import os
import sys
import pytest

print(os.path.join(os.getcwd(), "\\"))
sys.path.insert(len(sys.path), os.path.join(os.getcwd(), "\\"))
if False:
	from interval.iInterval import iInterval
from iInterval import iInterval


def test_iInterval_contains_value():
	a = iInterval(1, 2, True, True)
	assert a.contains_value(0.9) is False
	assert a.contains_value(1.0) is True
	assert a.contains_value(1.5) is True
	assert a.contains_value(2.0) is True
	assert a.contains_value(2.1) is False
	
	a = iInterval(1.0, 2.0, False, False)
	
	assert a.contains_value(0.0) is False
	assert a.contains_value(1.0) is False
	assert a.contains_value(1.000001) is True
	assert a.contains_value(1.999999) is True
	assert a.contains_value(2.0) is False
	assert a.contains_value(3.0) is False


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
