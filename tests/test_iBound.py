import pytest

from NicksIntervals.iBound import iBound, PART_OF_LEFT, PART_OF_RIGHT
from NicksIntervals.iInterval import iInterval
from random import shuffle


def test_iBound_order():
	assert (iBound(0, PART_OF_LEFT) < iBound(0, PART_OF_RIGHT)) is False
	assert (iBound(0, PART_OF_LEFT) < iBound(0, PART_OF_LEFT)) is False
	assert (iBound(0, PART_OF_RIGHT) < iBound(0, PART_OF_RIGHT)) is False
	assert (iBound(0, PART_OF_RIGHT) < iBound(0, PART_OF_LEFT)) is True
	
	assert (iBound(0, PART_OF_LEFT) == iBound(0, PART_OF_RIGHT)) is False
	assert (iBound(0, PART_OF_LEFT) == iBound(0, PART_OF_LEFT)) is True
	assert (iBound(0, PART_OF_RIGHT) == iBound(0, PART_OF_RIGHT)) is True
	assert (iBound(0, PART_OF_RIGHT) == iBound(0, PART_OF_LEFT)) is False
	
	assert (iBound(0, PART_OF_LEFT) > iBound(0, PART_OF_RIGHT)) is True
	assert (iBound(0, PART_OF_LEFT) > iBound(0, PART_OF_LEFT)) is False
	assert (iBound(0, PART_OF_RIGHT) > iBound(0, PART_OF_RIGHT)) is False
	assert (iBound(0, PART_OF_RIGHT) > iBound(0, PART_OF_LEFT)) is False


def test_iBound_interaction_with_builtin_sorted():
	bound_list = [
		iBound(1, PART_OF_RIGHT),
		iBound(2, PART_OF_RIGHT),
		iBound(3, PART_OF_RIGHT),
		iBound(3, PART_OF_LEFT),
		iBound(4, PART_OF_RIGHT),
		iBound(5, PART_OF_RIGHT),
	]
	
	# TODO: this is a crap way to test sorting but 20 shuffles should capture anything stupid.
	#  its really not even clear what is being tested here. I don't remember how this test works.
	for _ in range(0, 20):
		bound_list_shuffled_sorted = bound_list.copy()
		shuffle(bound_list_shuffled_sorted)
		bound_list_shuffled_sorted = list(sorted(bound_list_shuffled_sorted))
		# ensure all interval calls succeed without error
		for lower_bound, upper_bound in zip(bound_list_shuffled_sorted, bound_list_shuffled_sorted[1:]):
			iInterval(lower_bound, upper_bound)
		
		# ensure sorted list is the same as the starting list
		for bound, shuffled_bound in zip(bound_list, bound_list_shuffled_sorted):
			assert bound is shuffled_bound


# TODO: test Linked_iBound which has a different sorting mechanism