from __future__ import annotations
import itertools
import math
from typing import Iterable, TYPE_CHECKING, Generator, Tuple

# if TYPE_CHECKING:
from typing import Iterator

from NicksIntervals import util
from NicksIntervals.Linked_iBound import Linked_iBound
from NicksIntervals.iBound import iBound, iBound_Negative_Infinity, iBound_Positive_Infinity
import NicksIntervals.iInterval

iInterval = NicksIntervals.iInterval.iInterval

def subtract(a: Iterable[iInterval], b: Iterable[iInterval]) -> Iterable[iInterval]:
	# TODO: the performance of this algorithm on any multi_interval with many sub intervals is abysmal.
	#  must be reimplemented as a line-sweep for decent performance.
	result: Iterable[iInterval] = a
	
	for interval_b in b:
		# List constructor is called here to cause immediate evaluation of the generator.
		# Otherwise the reassignment to 'result' may trigger weird issues with closures on the next iteration of the for loop
		# This makes the execution eager, but we cant have our entire software consist of a giant lazy nested generator like in haskell I suppose.
		result = list(itertools.chain.from_iterable(subtract_atomic(interval_a, interval_b) for interval_a in result))
	
	# conversion from list to tuple is  unnecessary but promotes immutable patterns in usercode
	return tuple(result)


def subtract_atomic(a: iInterval, b: iInterval) -> Iterable[iInterval]:

	other_contains_self_lower_bound = contains_lower_bound_atomic(b, a.lower_bound)
	other_contains_self_upper_bound = contains_upper_bound_atomic(b, a.upper_bound)
	
	#   self:        ╠════╣
	#  other:  ╠════════════╣
	# result:
	if other_contains_self_lower_bound and other_contains_self_upper_bound:
		return tuple()
	
	self_contains_other_lower_bound = contains_lower_bound_atomic(a, b.lower_bound)
	self_contains_other_upper_bound = contains_upper_bound_atomic(a, b.upper_bound)
	
	#   self:  ╠════════════╣
	#  other:        ╠════╣
	# result:  ╠═════╡    ╞═╣
	if self_contains_other_lower_bound and self_contains_other_upper_bound:
		interim_result = []
		if a.lower_bound != b.lower_bound:
			interim_result.append(iInterval(a.lower_bound, b.lower_bound))
		if b.upper_bound != a.upper_bound:
			interim_result.append(iInterval(b.upper_bound, a.upper_bound))
		return tuple(interim_result)
	
	#   self:        ╠══════════╣
	#  other:  ╠════════════╣
	# result:               ╞═══╣
	if other_contains_self_lower_bound:
		if b.upper_bound != a.upper_bound:
			return tuple(iInterval(b.upper_bound, a.upper_bound))
	
	#   self:        ╠════╣
	#  other:  ╠════════════╣
	# result:
	# if other_contains_self_lower_bound and other_contains_self_upper_bound:
	# 	pass
	#   continue
	
	#   self:    ╠══════════╣
	#  other:        ╠════════════╣
	# result:    ╠═══╡
	if other_contains_self_upper_bound:
		if a.lower_bound != b.lower_bound:
			return tuple(iInterval(a.lower_bound, b.lower_bound))
	
	# if execution makes it past all above continues, the only remaining possibility is that the intervals are disjoint
	# in this case the entire first interval is output
	
	return tuple(a)


def intersect(a: Iterable[iInterval], b: Iterable[iInterval]) -> Iterable[iInterval]:
	# TODO: This will have abysmal performance on large datasets
	return subtract(a, exterior(b))


def intersect_atomic(a: iInterval, b: iInterval):

	self_contains_other_lower_bound = contains_lower_bound_atomic(a, b.lower_bound)
	self_contains_other_upper_bound = contains_upper_bound_atomic(a, b.upper_bound)
	
	#   self:  ╠════════════╣
	#  other:        ╠════╣
	# result:        ╠════╣
	if self_contains_other_lower_bound and self_contains_other_upper_bound:
		return b
	
	other_contains_self_lower_bound = contains_lower_bound_atomic(b, a.lower_bound)
	
	#   self:        ╠══════════╣
	#  other:  ╠════════════╣
	# result:        ╠══════╣
	if other_contains_self_lower_bound:
		return iInterval(a.lower_bound, b.upper_bound)
	
	other_contains_self_upper_bound = contains_upper_bound_atomic(b, a.upper_bound)
	
	#   self:        ╠════╣
	#  other:  ╠════════════╣
	# result:        ╠════╣
	if other_contains_self_lower_bound and other_contains_self_upper_bound:
		return a
	
	#   self:    ╠══════════╣
	#  other:        ╠════════════╣
	# result:        ╠══════╣
	if other_contains_self_upper_bound:
		return iInterval(b.lower_bound, a.upper_bound)
	
	return tuple()


def intersects(a: Iterable[iInterval], b: Iterable[iInterval]) -> bool:
	return any(intersects_atomic(a_interval, b_interval) for a_interval in a for b_interval in b)


def intersects_atomic(a: iInterval, b: iInterval) -> bool:
	return (
		a.contains_lower_bound(b.lower_bound) or
		a.contains_upper_bound(b.upper_bound) or
		b.contains_lower_bound(a.lower_bound) or
		b.contains_upper_bound(a.upper_bound)
	)


def touches(a: Iterable[iInterval], b: Iterable[iInterval]):
	if intersects(a, b):
		return False
	return any(touches_atomic(a_interval, b_interval) for a_interval in a for b_interval in b)


def touches_atomic(a: iInterval, b: iInterval) -> bool:
	if math.isclose(a.lower_bound.value, b.upper_bound.value) and (a.lower_bound.part_of_right == b.upper_bound.part_of_right):
		return True
	if math.isclose(a.upper_bound.value, b.lower_bound.value) and (a.upper_bound.part_of_left == b.lower_bound.part_of_left):
		return True
	return False


def contains_value(a: Iterable[iInterval], value: float) -> bool:
	return any(contains_value_atomic(interval, value) for interval in a)


def contains_value_atomic(a: iInterval, value: float) -> bool:
	if math.isclose(a.lower_bound.value, value) and a.lower_bound.part_of_right:
		return True
	elif math.isclose(a.upper_bound.value, value) and a.upper_bound.part_of_left:
		return True
	elif a.lower_bound < value < a.upper_bound:
		return True
	return False


def contains_interval(a: Iterable[iInterval], b: Iterable[iInterval]) -> bool:
	return all(
		any(contains_interval_atomic(a_interval, b_interval) for a_interval in a) for b_interval in b
	)


def contains_interval_atomic(a: iInterval, b: iInterval) -> bool:
	if a.is_degenerate and b.is_degenerate and math.isclose(a.lower_bound.value, b.lower_bound.value):
		return True
	else:
		return contains_lower_bound_atomic(a, b.lower_bound) and contains_lower_bound_atomic(a, b.upper_bound)


def contains_upper_bound_atomic(a: iInterval, bound: iBound) -> bool:
	if a.is_degenerate and math.isclose(a.lower_bound.value, bound.value):
		return bound.part_of_left
	else:
		if math.isclose(a.lower_bound.value, bound.value):
			return a.lower_bound.part_of_right and bound.part_of_left
		if math.isclose(a.upper_bound.value, bound.value):
			return not (a.upper_bound.part_of_right and bound.part_of_left)
		elif a.lower_bound < bound < a.upper_bound:
			return True
	return False


def contains_lower_bound_atomic(a: iInterval, bound: iBound) -> bool:
	if a.is_degenerate and math.isclose(a.upper_bound.value, bound.value):
		return bound.part_of_right
	else:
		if math.isclose(a.lower_bound.value, bound.value):
			return not (a.lower_bound.part_of_left and bound.part_of_right)
		if math.isclose(a.upper_bound.value, bound.value):
			return a.upper_bound.part_of_left and bound.part_of_right
		if a.lower_bound < bound < a.upper_bound:
			return True
	return False


def left_exterior_atomic(a: iInterval) -> Iterable[iInterval]:
	if a.lower_bound == iBound_Negative_Infinity:
		return tuple()
	else:
		return iInterval(iBound_Negative_Infinity, a.lower_bound)


def right_exterior_atomic(a: iInterval) -> Iterable[iInterval]:
	if a.upper_bound == iBound_Positive_Infinity:
		return tuple()
	else:
		return iInterval(a.upper_bound, iBound_Positive_Infinity)


def exterior_atomic(a: iInterval) -> Iterable[iInterval]:
	return tuple(itertools.chain(left_exterior_atomic(a), right_exterior_atomic(a)))


def exterior(a: Iterable[iInterval]) -> Iterable[iInterval]:
	# TODO: the implementation in iMulti_iInterval is more efficient for large datasets but may actually be less correct?
	#  testing shows the performance of the solution below is very bad. Every item of the results list is compared with every item of the results list over and over
	#  to make this approach efficient the subtract function would need to be reimplemented as a line sweep function
	return subtract(iInterval.complete(), a)


def hull(a: Iterable[iInterval]) -> Iterable[iInterval]:
	result = tuple()
	first = True
	for a_interval in a:
		if first:
			result = a_interval
		else:
			hull_atomic(result, a_interval)
	return result
	

def hull_atomic(a: iInterval, b: iInterval) -> iInterval:
	return iInterval(min(a.lower_bound, b.lower_bound), max(a.upper_bound, b.upper_bound))


##############################################
# LINE SWEEP FUNCTIONS:
#############################################

def get_sorted_linked_bounds_with_stack_height(a: Iterable[iInterval]) -> Generator[Tuple[int, Linked_iBound, int], None, None]:
	"""
	Returns a generator yielding tuples;
	(
		stack_height_before:int
		bound:Linked_iBound
		stack_height_after:int
	)
	"""
	sorted_linked_bounds = sorted(itertools.chain.from_iterable(interval.get_linked_bounds() for interval in a))
	stack_count_before = 0
	stack_count_after = 0
	for previous_bound, current_bound, next_bound in util.iter_previous_and_next(sorted_linked_bounds):
		if current_bound.is_lower_bound:
			stack_count_after += 1
		else:
			stack_count_after -= 1
		yield stack_count_before, current_bound, stack_count_after
		stack_count_before = stack_count_after

	
def iter_bound_pairs(a: Iterable[iInterval]) -> Iterator[Tuple[iBound, iBound, bool]]:
	"""
	iterates over each pair of bounds in all intervals returning a tuple
	pairs of bounds that do not form a valid interval are ignored.
	adds infinities to the exterior as required.
	(
		previous_bound: iBound,
		next_bound: iBound,
		is_interior_interval: bool
	)
	"""
	INTERIOR = True
	EXTERIOR = False
	for ((_, prev_bound, _), (stack_before, bound, stack_after), (_, next_bound, _)) in util.iter_previous_and_next(get_sorted_linked_bounds_with_stack_height(a), (None, None, None)):
		if prev_bound is None:
			if bound != iBound_Negative_Infinity:
				yield iBound_Negative_Infinity, bound.bound, EXTERIOR
		else:
			if prev_bound.bound != bound.bound:
				yield prev_bound.bound, bound.bound, EXTERIOR if stack_before == 0 else INTERIOR
		
		if next_bound is None:
			if bound != iBound_Positive_Infinity:
				yield bound.bound, iBound_Positive_Infinity, EXTERIOR


def iter_bound_pairs_merge_touching(a: Iterable[iInterval]) -> Iterator[Tuple[iBound, iBound, bool]]:
	for is_interior, group in itertools.groupby(iter_bound_pairs(a), lambda item: item[2]):
		(first_bound, _, _), (_, last_bound, _) = util.first_and_last(group)
		yield first_bound, last_bound, is_interior
