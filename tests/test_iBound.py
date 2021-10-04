import pytest

from nicks_intervals.Bound import Bound, PART_OF_LEFT, PART_OF_RIGHT
from nicks_intervals.Interval import Interval
from random import shuffle


def test_iBound_order():
	assert (Bound(0, PART_OF_LEFT) < Bound(0, PART_OF_RIGHT)) is False
	assert (Bound(0, PART_OF_LEFT) < Bound(0, PART_OF_LEFT)) is False
	assert (Bound(0, PART_OF_RIGHT) < Bound(0, PART_OF_RIGHT)) is False
	assert (Bound(0, PART_OF_RIGHT) < Bound(0, PART_OF_LEFT)) is True
	
	assert (Bound(0, PART_OF_LEFT) == Bound(0, PART_OF_RIGHT)) is False
	assert (Bound(0, PART_OF_LEFT) == Bound(0, PART_OF_LEFT)) is True
	assert (Bound(0, PART_OF_RIGHT) == Bound(0, PART_OF_RIGHT)) is True
	assert (Bound(0, PART_OF_RIGHT) == Bound(0, PART_OF_LEFT)) is False
	
	assert (Bound(0, PART_OF_LEFT) > Bound(0, PART_OF_RIGHT)) is True
	assert (Bound(0, PART_OF_LEFT) > Bound(0, PART_OF_LEFT)) is False
	assert (Bound(0, PART_OF_RIGHT) > Bound(0, PART_OF_RIGHT)) is False
	assert (Bound(0, PART_OF_RIGHT) > Bound(0, PART_OF_LEFT)) is False


def test_iBound_interaction_with_builtin_sorted():
	bound_list = [
		Bound(1, PART_OF_RIGHT),
		Bound(2, PART_OF_RIGHT),
		Bound(3, PART_OF_RIGHT),
		Bound(3, PART_OF_LEFT),
		Bound(4, PART_OF_RIGHT),
		Bound(5, PART_OF_RIGHT),
	]
	
	# TODO: this is a crap way to test sorting but 20 shuffles should capture anything stupid.
	#  its really not even clear what is being tested here. I don't remember how this test works.
	for _ in range(0, 20):
		bound_list_shuffled_sorted = bound_list.copy()
		shuffle(bound_list_shuffled_sorted)
		bound_list_shuffled_sorted = list(sorted(bound_list_shuffled_sorted))
		# ensure all interval calls succeed without error
		for lower_bound, upper_bound in zip(bound_list_shuffled_sorted, bound_list_shuffled_sorted[1:]):
			Interval(lower_bound, upper_bound)
		
		# ensure sorted list is the same as the starting list
		for bound, shuffled_bound in zip(bound_list, bound_list_shuffled_sorted):
			assert bound is shuffled_bound


# TODO: test Linked_iBound which has a different sorting mechanism