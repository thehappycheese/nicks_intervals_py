from typing import Collection, Union

import pytest

from nicks_intervals.Bound import Bound, PART_OF_LEFT, PART_OF_RIGHT
from nicks_intervals.Interval import Interval
from nicks_intervals.Multi_Interval import Multi_Interval


def exterior_is_same_as_inf_sub(a: Union[Interval, Multi_Interval]):
	return a.exterior == Interval.inf().subtract(a)


def interior_is_the_same_as_inf_sub_inf_sub(a: Union[Interval, Multi_Interval]):
	return a.interior == Interval.inf().subtract(Interval.inf().subtract(a))


def test_iInterval_exterior():
	assert exterior_is_same_as_inf_sub(Interval.open(1, 2)) is True
	assert exterior_is_same_as_inf_sub(Interval.closed(1, 2)) is True
	assert exterior_is_same_as_inf_sub(Interval.inf_open(1)) is True
	assert exterior_is_same_as_inf_sub(Interval.open_inf(2)) is True


def test_iInterval_interior():
	assert interior_is_the_same_as_inf_sub_inf_sub(Interval.open(1, 2)) is True
	assert interior_is_the_same_as_inf_sub_inf_sub(Interval.closed(1, 2)) is True
	assert interior_is_the_same_as_inf_sub_inf_sub(Interval.inf_open(1)) is True
	assert interior_is_the_same_as_inf_sub_inf_sub(Interval.open_inf(2)) is True


def test_iMulti_iInterval_exterior():
	assert exterior_is_same_as_inf_sub(Multi_Interval([Interval.open(1, 2)])) is True
	assert exterior_is_same_as_inf_sub(Multi_Interval([Interval.closed(1, 2)])) is True
	assert exterior_is_same_as_inf_sub(Multi_Interval([Interval.inf_open(1)])) is True
	assert exterior_is_same_as_inf_sub(Multi_Interval([Interval.open_inf(2)])) is True
	# TODO: create some harder test cases
	assert exterior_is_same_as_inf_sub(Multi_Interval([Interval.open_inf(2), Interval.open(0, 2), Interval.closed(3, 5), Interval.closed(4, 5), Interval.open(3, 4)])) is True
