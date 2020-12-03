import pytest

from NicksIntervals.Bound import Bound, PART_OF_LEFT, PART_OF_RIGHT
from NicksIntervals.Interval import Interval


def test_iInterval_init_argtype():
	with pytest.raises(TypeError):
		Interval.closed(1, 'a')
	with pytest.raises(TypeError):
		Interval.closed(1, 'a')
	with pytest.raises(TypeError):
		Interval(1.0, 2)
	with pytest.raises(TypeError):
		Interval(1.0, 2.0)
	
	Interval(Bound(0, False), Bound(1, True))


def test_iInterval_init_reversed_not_permitted():
	with pytest.raises(Exception):
		Interval(Bound(1, PART_OF_RIGHT), Bound(0, PART_OF_RIGHT))


def test_iInterval_init_degenerate_must_be_closed():
	# degenerate intervals may not have any open bounds
	with pytest.raises(Exception):
		Interval(Bound(0, PART_OF_LEFT), Bound(0, PART_OF_LEFT))
	with pytest.raises(Exception):
		Interval(Bound(0, PART_OF_LEFT), Bound(0, PART_OF_RIGHT))
	with pytest.raises(Exception):
		Interval(Bound(0, PART_OF_RIGHT), Bound(0, PART_OF_RIGHT))
		
	Interval(Bound(0, PART_OF_RIGHT), Bound(0, PART_OF_LEFT))


def test_iInterval_init_infinitesimal():
	with pytest.raises(Exception):
		assert Interval.closed(1, 1.000000000000000001).has_infinitesimal


def test_iInterval_degenerate_constructor():
	m = Interval.degenerate(0)
	assert m.has_degenerate is True
	with pytest.raises(Exception):
		Interval.degenerate(float('-inf'))
	with pytest.raises(Exception):
		Interval.degenerate(float('inf'))


def test_iInterval_open_constructor():
	m = Interval.open(1, 2)
	assert m.contains_value(1) is False
	assert m.contains_value(2) is False
	assert m.lower_bound.part_of_left is True
	assert m.upper_bound.part_of_right is True


def test_iInterval_closed_constructor():
	m = Interval.closed(1, 2)
	assert m.contains_value(1) is True
	assert m.contains_value(2) is True
	assert m.lower_bound.part_of_right is True
	assert m.upper_bound.part_of_left is True

	
def test_iInterval_open_closed_constructor():
	m = Interval.open_closed(1, 2)
	assert m.contains_value(1) is False
	assert m.contains_value(2) is True
	assert m.lower_bound.part_of_left is True
	assert m.upper_bound.part_of_left is True


def test_iInterval_closed_open_constructor():
	m = Interval.closed_open(1, 2)
	assert m.contains_value(1) is True
	assert m.contains_value(2) is False
	assert m.lower_bound.part_of_right is True
	assert m.upper_bound.part_of_right is True