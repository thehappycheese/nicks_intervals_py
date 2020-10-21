import pytest

from NicksIntervals.iBound import iBound, PART_OF_LEFT, PART_OF_RIGHT
from NicksIntervals.iInterval import iInterval


def test_iInterval_init_argtype():
	with pytest.raises(TypeError):
		iInterval.closed(1, 'a')
	with pytest.raises(TypeError):
		iInterval.closed(1, 'a')
	with pytest.raises(TypeError):
		iInterval(1.0, 2)
	with pytest.raises(TypeError):
		iInterval(1.0, 2.0)
	
	iInterval(iBound(0, False), iBound(1, True))


def test_iInterval_init_reversed_not_permitted():
	with pytest.raises(Exception):
		iInterval(iBound(1, PART_OF_RIGHT), iBound(0, PART_OF_RIGHT))


def test_iInterval_init_degenerate_must_be_closed():
	# degenerate intervals may not have any open bounds
	with pytest.raises(Exception):
		iInterval(iBound(0, PART_OF_LEFT), iBound(0, PART_OF_LEFT))
	with pytest.raises(Exception):
		iInterval(iBound(0, PART_OF_LEFT), iBound(0, PART_OF_RIGHT))
	with pytest.raises(Exception):
		iInterval(iBound(0, PART_OF_RIGHT), iBound(0, PART_OF_RIGHT))
		
	iInterval(iBound(0, PART_OF_RIGHT), iBound(0, PART_OF_LEFT))


def test_iInterval_init_infinitesimal():
	with pytest.raises(Exception):
		assert iInterval.closed(1, 1.000000000000000001).is_infinitesimal


def test_iInterval_degenerate_constructor():
	m = iInterval.degenerate(0)
	assert m.is_degenerate is True
	with pytest.raises(Exception):
		iInterval.degenerate(float('-inf'))
	with pytest.raises(Exception):
		iInterval.degenerate(float('inf'))


def test_iInterval_open_constructor():
	m = iInterval.open(1, 2)
	assert m.contains_value(1) is False
	assert m.contains_value(2) is False
	assert m.lower_bound.part_of_left is True
	assert m.upper_bound.part_of_right is True


def test_iInterval_closed_constructor():
	m = iInterval.closed(1, 2)
	assert m.contains_value(1) is True
	assert m.contains_value(2) is True
	assert m.lower_bound.part_of_right is True
	assert m.upper_bound.part_of_left is True

	
def test_iInterval_open_closed_constructor():
	m = iInterval.open_closed(1, 2)
	assert m.contains_value(1) is False
	assert m.contains_value(2) is True
	assert m.lower_bound.part_of_left is True
	assert m.upper_bound.part_of_left is True


def test_iInterval_closed_open_constructor():
	m = iInterval.closed_open(1, 2)
	assert m.contains_value(1) is True
	assert m.contains_value(2) is False
	assert m.lower_bound.part_of_right is True
	assert m.upper_bound.part_of_right is True