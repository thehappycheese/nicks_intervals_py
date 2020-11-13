from typing import Collection

import pytest

from NicksIntervals.iBound import iBound, PART_OF_LEFT, PART_OF_RIGHT
from NicksIntervals.iInterval import iInterval
from NicksIntervals.iMulti_iInterval import iMulti_iInterval


def exterior_is_same_as_inf_sub(a: Collection[iInterval]):
	return a.exterior == iInterval.inf().subtract(a)


def interior_is_the_same_as_inf_sub_inf_sub(a: Collection[iInterval]):
	return a.interior == iInterval.inf().subtract(iInterval.inf().subtract(a))


def test_iInterval_exterior():
	assert exterior_is_same_as_inf_sub(iInterval.open(1, 2)) is True
	assert exterior_is_same_as_inf_sub(iInterval.closed(1, 2)) is True
	assert exterior_is_same_as_inf_sub(iInterval.inf_open(1)) is True
	assert exterior_is_same_as_inf_sub(iInterval.open_inf(2)) is True


def test_iInterval_interior():
	assert interior_is_the_same_as_inf_sub_inf_sub(iInterval.open(1, 2)) is True
	assert interior_is_the_same_as_inf_sub_inf_sub(iInterval.closed(1, 2)) is True
	assert interior_is_the_same_as_inf_sub_inf_sub(iInterval.inf_open(1)) is True
	assert interior_is_the_same_as_inf_sub_inf_sub(iInterval.open_inf(2)) is True


def test_iMulti_iInterval_exterior():
	assert exterior_is_same_as_inf_sub(iMulti_iInterval([iInterval.open(1, 2)])) is True
	assert exterior_is_same_as_inf_sub(iMulti_iInterval([iInterval.closed(1, 2)])) is True
	assert exterior_is_same_as_inf_sub(iMulti_iInterval([iInterval.inf_open(1)])) is True
	assert exterior_is_same_as_inf_sub(iMulti_iInterval([iInterval.open_inf(2)])) is True
	# TODO: create some harder test cases
	assert exterior_is_same_as_inf_sub(iMulti_iInterval([iInterval.open_inf(2), iInterval.open(0, 2), iInterval.closed(3, 5), iInterval.closed(4, 5), iInterval.open(3, 4)])) is True
