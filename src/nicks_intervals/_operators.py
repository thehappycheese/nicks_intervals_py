from __future__ import annotations

import itertools
import math
from typing import TypeVar, Generator, Tuple, TYPE_CHECKING, List, Sized, Collection, Union, Iterable, Iterator, Callable, Sequence, Optional

from . import util
from .Bound import Bound, iBound_Negative_Infinity, iBound_Positive_Infinity, Linked_Bound


if TYPE_CHECKING:
	from .Interval_Map import Interval_Map
	from .Interval import Interval
	from .Interval import Linked_Interval
	from .Multi_Interval import Multi_Interval

T = TypeVar('T')


def scaled(a: Iterable[Interval], scale_factor: float) -> Collection[Interval]:
	from .Interval import Interval
	return [Interval(a_interval.lower_bound.scaled(scale_factor), a_interval.upper_bound.scaled(scale_factor)) for a_interval in a]


def translated(a: Iterable[Interval], translation: float) -> Collection[Interval]:
	from .Interval import Interval
	return [Interval(a_interval.lower_bound.translated(translation), a_interval.upper_bound.translated(translation)) for a_interval in a]


def scaled_then_translated(a: Iterable[Interval], scale_factor: float, translation: float):
	from .Interval import Interval
	return [Interval(a_interval.lower_bound.scaled_then_translated(scale_factor, translation), a_interval.upper_bound.scaled_then_translated(scale_factor, translation)) for a_interval in a]


def translated_then_scaled(a: Iterable[Interval], translation: float, scale_factor: float):
	from .Interval import Interval
	return [Interval(a_interval.lower_bound.translated_then_scaled(translation, scale_factor), a_interval.upper_bound.translated_then_scaled(translation, scale_factor)) for a_interval in a]


def apply_interval_map_to_interval_atomic(map_from: Interval, map_to: Interval, interval: Interval) -> Collection[Interval]:
	
	if map_from.length == 0:
		if intersects(map_from, interval):
			return [map_to]
		else:
			return []
	scale_factor = map_to.length / map_from.length
	return [* intersect(  # this intersect with map_to required? Yes: it confirms that the bound directions of the result comply with map_to
			scaled_then_translated(
				translated(
					intersect(map_from, interval),
					-map_from.lower_bound.value
				),
				scale_factor,
				map_to.lower_bound.value
			),
			map_to
		)
	]


def apply_interval_maps_to_intervals(iterable_of_links: Iterable[Sequence[Interval]], a: Iterable[Interval]) -> Collection[Interval]:
	result = []
	for a_interval in a:
		for link_sequence in iterable_of_links:
			result.extend(apply_interval_map_to_interval_atomic(link_sequence[0], link_sequence[-1], a_interval))
	return result


def apply_interval_map_to_value_atomic(map_from: Interval, map_to: Interval, value: float) -> Tuple[float, ...]:
	if contains_value_atomic(map_from, value):
		scale_factor = map_to.length / map_from.length
		result_value = (value-map_from.lower_bound.value) * scale_factor + map_to.lower_bound.value
		if contains_value_atomic(map_to, result_value):
			return (result_value, )
	return tuple()


def apply_interval_maps_to_value(iterable_of_links: Iterable[Sequence[Interval]], value: float) -> Sequence[float]:
	result = []
	for link_sequence in iterable_of_links:
		result.extend(apply_interval_map_to_value_atomic(link_sequence[0], link_sequence[-1], value))
	return result


# TODO: The term 'degenerate' is a bit ambiguous. Is it preferable to change all code to use iInterval.length == 0? This is easier to understand at a glance.
def is_degenerate_atomic(a: Interval):
	if a.lower_bound.value == a.upper_bound.value:
		if a.lower_bound.part_of_right and a.upper_bound.part_of_left:  # TODO: it is impossible to construct an interval that does not meet condition, if the above condition is met. This check is redundant
			return True
	return False


def has_degenerate(a: Collection[Interval]):
	return any(is_degenerate_atomic(a_interval) for a_interval in a)


def get_bounds(a: Iterable[Interval]) -> List[Bound]:
	return list(
		itertools.chain.from_iterable([
			a_interval.lower_bound,
			a_interval.upper_bound
			] for a_interval in a))


def get_linked_bounds(a: Iterable[Interval]) -> List[Linked_Bound]:
	return list(
		itertools.chain.from_iterable((
			a_interval.lower_bound.get_Linked_iBound(linked_interval=a_interval, is_lower_bound=True),
			a_interval.upper_bound.get_Linked_iBound(linked_interval=a_interval, is_lower_bound=False
		)) for a_interval in a))


def get_linked_intervals(a: Iterable[Interval], linked_objects: Iterable[T]) -> Iterable[Linked_Interval[T]]:
	from .Interval import Linked_Interval
	return list(Linked_Interval(a_interval, linked_objects) for a_interval in a)


def is_complete(a: Collection[Interval]) -> bool:
	bounds = sorted(get_bounds(a))
	if len(bounds) < 2:
		return False
	return bounds[0] == iBound_Negative_Infinity and bounds[-1] == iBound_Positive_Infinity


def is_empty(a: Sized[Interval]):
	return len(a) == 0


def subtract_based_on_atomics(a: Iterable[Interval], b: Iterable[Interval]) -> Collection[Interval]:
	# The performance of this algorithm on any multi_interval with many sub intervals is abysmal.
	#  must be reimplemented as a line-sweep for decent performance. This stays here for testing purposes.
	result = a
	
	for interval_b in b:
		# List constructor is called here to cause immediate evaluation of the generator.
		# Otherwise the reassignment to 'result' may trigger weird issues with closures on the next iteration of the for loop
		# This makes the execution eager, but we cant have our entire software consist of a giant lazy nested generator like in haskell I suppose.
		result = list(itertools.chain.from_iterable(subtract_atomic(interval_a, interval_b) for interval_a in result))
	
	return result


def subtract_and_flatten(minuend: Iterable[Interval], subtrahend: Iterable[Interval]) -> Collection[Interval]:
	""" minuend - subtrahend = difference
	"""
	# TODO: this function is a bit useless since it causes potentially unwanted flattening of the minuend if the minuend is a multi-interval
	#  instead, an algorithm must be developed which tracks the content of the minuend stack, not just the stack height
	
	bound_list = []
	
	sorted_link_bounds = sorted(itertools.chain(get_linked_bounds(get_linked_intervals(minuend, minuend)), get_linked_bounds(get_linked_intervals(subtrahend, subtrahend))))
	
	minuend_stack_count_before = 0
	minuend_stack_count_after = 0
	subtrahend_stack_count_before = 0
	subtrahend_stack_count_after = 0
	for current_bound in sorted_link_bounds:
		if current_bound.interval._linked_objects is minuend:
			if current_bound.is_lower_bound:
				minuend_stack_count_after += 1
			else:
				minuend_stack_count_after -= 1
		elif current_bound.interval._linked_objects is subtrahend:
			if current_bound.is_lower_bound:
				subtrahend_stack_count_after += 1
			else:
				subtrahend_stack_count_after -= 1
		# TODO: This if statement is untested and very likely to be wrong.
		if ((minuend_stack_count_after > 0 and subtrahend_stack_count_before > 0 and subtrahend_stack_count_after == 0) or
				(minuend_stack_count_before == 0 and minuend_stack_count_after > 0 and subtrahend_stack_count_before == 0 and subtrahend_stack_count_after == 0) or
				(minuend_stack_count_before > 0 and subtrahend_stack_count_before == 0 and subtrahend_stack_count_after > 0) or
				(minuend_stack_count_before > 0 and minuend_stack_count_after == 0 and subtrahend_stack_count_before == 0 and subtrahend_stack_count_after == 0)):
			bound_list.append(current_bound)
		minuend_stack_count_before = minuend_stack_count_after
		subtrahend_stack_count_before = subtrahend_stack_count_after

	from .Interval import Interval
	return [Interval(lower_bound, upper_bound) for lower_bound, upper_bound in util.iter_consecutive_disjoint_pairs(bound_list) if lower_bound != upper_bound]


def subtract(minuend: Iterable[Interval], subtrahend: Iterable[Interval]) -> Collection[Interval]:
	from .Interval import Interval
	# minuend - subtrahend = difference
	result = []
	
	# TODO: the pollution of the interval class with this linked object idea was not good and needs to be walked back.
	#  the only significant place it is used is here... and a few other places that don't matter as much.
	#  linked bounds will still be needed due to thier sorting behaviour, unless we make a function that does
	#  that on something like a List[Tuple[bound:iBound, is_lower:bool, interval:Interval]]
	sorted_link_bounds = sorted(itertools.chain(get_linked_bounds(get_linked_intervals(minuend, [minuend])), get_linked_bounds(get_linked_intervals(subtrahend, [subtrahend]))))
	
	minuend_intervals_awaiting_lower_bound: List[Interval] = []
	minuend_intervals_awaiting_upper_bound: List[Tuple[Interval, Linked_Bound]] = []
	
	subtrahend_stack_count_previous = 0
	subtrahend_stack_count = 0
	
	for current_bound in sorted_link_bounds:
		if current_bound.interval.linked_objects[0] is subtrahend:
			if current_bound.is_lower_bound:
				subtrahend_stack_count += 1
			else:
				subtrahend_stack_count -= 1
				
		elif current_bound.interval.linked_objects[0] is minuend:
			if current_bound.is_lower_bound:
				if subtrahend_stack_count > 0:
					minuend_intervals_awaiting_lower_bound.append(current_bound.interval)
				else:
					minuend_intervals_awaiting_upper_bound.append((current_bound.interval, current_bound))
			else:  # current_bound.is_upper_bound
				try:
					# this interval was entirely overlapped by the subtrahend, and never found a starting bound. no further action required as it is not to be in the output
					minuend_intervals_awaiting_lower_bound.remove(current_bound.interval)
				except:
					# this interval did find a lower bound, it must be added to the output.
					interval_to_close = next(item for item in minuend_intervals_awaiting_upper_bound if item[0] == current_bound.interval)
					minuend_intervals_awaiting_upper_bound.remove(interval_to_close)
					if interval_to_close[1].bound != current_bound.bound:  # TODO: is this if statement necessary?
						result.append(Interval(interval_to_close[1].bound, current_bound.bound))
		
		if subtrahend_stack_count > 0 and subtrahend_stack_count_previous == 0:  # a lower bound of subtrahend
			# the current bound should be used to terminate all intervals in awaiting_upper_bound, and all these intervals should be moved into awaiting lower bound.
			for awaiting_upper_bound in minuend_intervals_awaiting_upper_bound:
				minuend_intervals_awaiting_lower_bound.append(awaiting_upper_bound[0])
				if awaiting_upper_bound[1].bound != current_bound.bound:
					result.append(Interval(awaiting_upper_bound[1].bound, current_bound.bound))
			minuend_intervals_awaiting_upper_bound = []
		elif subtrahend_stack_count == 0 and subtrahend_stack_count_previous > 0:  # an upper bound of subtrahend
			# the current bound should be used to start all intervals in awaiting lower bound, and they should be moved into awaiting upper bound
			for awaiting_lower_bound in minuend_intervals_awaiting_lower_bound:
				minuend_intervals_awaiting_upper_bound.append((awaiting_lower_bound, current_bound))
			minuend_intervals_awaiting_lower_bound = []
		
		subtrahend_stack_count_previous = subtrahend_stack_count
		
	return result


def subtract_atomic(a: Interval, b: Interval) -> Collection[Interval]:
	from .Interval import Interval
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
			interim_result.append(Interval(a.lower_bound, b.lower_bound))
		if b.upper_bound != a.upper_bound:
			interim_result.append(Interval(b.upper_bound, a.upper_bound))
		return tuple(interim_result)
	
	#   self:        ╠══════════╣
	#  other:  ╠════════════╣
	# result:               ╞═══╣
	if other_contains_self_lower_bound:
		if b.upper_bound != a.upper_bound:
			return tuple(Interval(b.upper_bound, a.upper_bound))
	
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
			return tuple(Interval(a.lower_bound, b.lower_bound))
	
	# if execution makes it past all above continues, the only remaining possibility is that the intervals are disjoint
	# in this case the entire first interval is output
	
	return a


def intersect(a: Collection[Interval], b: Collection[Interval]) -> Collection[Interval]:
	# TODO: This will have abysmal performance on large datasets
	#  I think it can be implemented as a sweep over linked bounds?
	return subtract(a, exterior(b))


def intersect_atomic(a: Interval, b: Interval) -> Collection[Interval]:
	from .Interval import Interval
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
		return Interval(a.lower_bound, b.upper_bound)
	
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
		return Interval(b.lower_bound, a.upper_bound)
	
	return tuple()


def intersects(a: Collection[Interval], b: Collection[Interval]) -> bool:
	return any(intersects_atomic(a_interval, b_interval) for a_interval in a for b_interval in b)


def intersects_atomic(a: Interval, b: Interval) -> bool:
	return (
		contains_lower_bound_atomic(a, b.lower_bound) or
		contains_upper_bound_atomic(a, b.upper_bound) or
		contains_lower_bound_atomic(b, a.lower_bound) or
		contains_upper_bound_atomic(b, a.upper_bound)
	)


def touches(a: Collection[Interval], b: Collection[Interval]):
	if intersects(a, b):
		return False
	return any(touches_atomic(a_interval, b_interval) for a_interval in a for b_interval in b)


def touches_atomic(a: Interval, b: Interval) -> bool:
	if math.isclose(a.lower_bound.value, b.upper_bound.value) and (a.lower_bound.part_of_right == b.upper_bound.part_of_right):
		return True
	if math.isclose(a.upper_bound.value, b.lower_bound.value) and (a.upper_bound.part_of_left == b.lower_bound.part_of_left):
		return True
	return False


def nearest_contained_value(a: Collection[Interval], value: float, containment_amount: float = 0.000001):
	"""does not account for bound direction"""
	nearest_value_so_far = None
	nearest_so_far_dist = float('inf')
	
	for interval in a:
		if contains_value_atomic(interval, value):
			return value
		else:
			if value < interval.lower_bound.value or math.isclose(value, interval.lower_bound.value):
				diff = abs(value - interval.lower_bound.value)
				if diff < nearest_so_far_dist:
					nearest_so_far_dist = diff
					nearest_value_so_far = interval.lower_bound.value + (containment_amount if interval.lower_bound.part_of_left else 0)
			
			elif value >= interval.upper_bound.value or math.isclose(value, interval.upper_bound.value):
				diff = abs(value - interval.upper_bound.value)
				if diff < nearest_so_far_dist:
					nearest_so_far_dist = diff
					nearest_value_so_far = interval.upper_bound.value - (containment_amount if interval.upper_bound.part_of_right else 0)
	
	return nearest_value_so_far
	

def contains_value(a: Collection[Interval], value: float) -> bool:
	return any(contains_value_atomic(interval, value) for interval in a)


def contains_value_atomic(a: Interval, value: float) -> bool:
	if math.isclose(a.lower_bound.value, value) and a.lower_bound.part_of_right:
		return True
	elif math.isclose(a.upper_bound.value, value) and a.upper_bound.part_of_left:
		return True
	elif a.lower_bound.value < value < a.upper_bound.value:
		return True
	return False


def contains_interval(a: Collection[Interval], b: Collection[Interval]) -> bool:
	return all(
		any(contains_interval_atomic(a_interval, b_interval) for a_interval in a) for b_interval in b
	)


def contains_interval_atomic(a: Interval, b: Interval) -> bool:
	if is_degenerate_atomic(a) and is_degenerate_atomic(b) and math.isclose(a.lower_bound.value, b.lower_bound.value):
		return True
	else:
		return contains_lower_bound_atomic(a, b.lower_bound) and contains_upper_bound_atomic(a, b.upper_bound)


def contains_upper_bound_atomic(a: Interval, upper_bound: Bound) -> bool:
	if is_degenerate_atomic(a) and math.isclose(a.lower_bound.value, upper_bound.value):
		return upper_bound.part_of_left
	else:
		if math.isclose(a.lower_bound.value, upper_bound.value):
			return a.lower_bound.part_of_right and upper_bound.part_of_left
		if math.isclose(a.upper_bound.value, upper_bound.value):
			return not (a.upper_bound.part_of_right and upper_bound.part_of_left)
		elif a.lower_bound < upper_bound < a.upper_bound:
			return True
	return False


def contains_lower_bound_atomic(a: Interval, lower_bound: Bound) -> bool:
	if is_degenerate_atomic(a) and math.isclose(a.upper_bound.value, lower_bound.value):
		return lower_bound.part_of_right
	else:
		if math.isclose(a.lower_bound.value, lower_bound.value):
			return not (a.lower_bound.part_of_left and lower_bound.part_of_right)
		if math.isclose(a.upper_bound.value, lower_bound.value):
			return a.upper_bound.part_of_left and lower_bound.part_of_right
		if a.lower_bound < lower_bound < a.upper_bound:
			return True
	return False


def left_exterior_atomic(a: Interval) -> Collection[Interval]:
	if a.lower_bound == iBound_Negative_Infinity:
		return tuple()
	else:
		from .Interval import Interval
		return Interval(iBound_Negative_Infinity, a.lower_bound)


def right_exterior_atomic(a: Interval) -> Collection[Interval]:
	if a.upper_bound == iBound_Positive_Infinity:
		return tuple()
	else:
		from .Interval import Interval
		return Interval(a.upper_bound, iBound_Positive_Infinity)


def exterior_atomic(a: Interval) -> Collection[Interval]:
	return tuple(itertools.chain(left_exterior_atomic(a), right_exterior_atomic(a)))


def exterior(a: Collection[Interval]) -> Collection[Interval]:
	from .Interval import Interval
	return coerce_collection_to_Interval_or_Multi_Interval([
		Interval(lower_bound, upper_bound)
		for lower_bound, upper_bound, is_interior
		in iter_bound_pairs(a)
		if not is_interior
	])


def interior(a: Collection[Interval]) -> Collection[Interval]:
	from .Interval import Interval
	return [Interval(lower_bound, upper_bound)
			for lower_bound, upper_bound, is_interior
			in iter_bound_pairs(a)
			if is_interior
	]


def interior_merged(self) -> Collection[Interval]:
	from .Interval import Interval
	return [
		Interval(lower_bound, upper_bound)
		for lower_bound, upper_bound, is_interior
		in iter_bound_pairs_merge_touching(self)
		if is_interior
	]


def hull(a: Iterable[Interval]) -> Collection[Interval]:
	result = tuple()
	first = True
	for a_interval in a:
		if first:
			result = a_interval
			first = False
		else:
			result = hull_atomic(result, a_interval)
	return result
	

def hull_atomic(a: Interval, b: Interval) -> Interval:
	from .Interval import Interval
	return Interval(min(a.lower_bound, b.lower_bound), max(a.upper_bound, b.upper_bound))


##############################################
# LINE SWEEP FUNCTIONS:
#############################################

def get_sorted_linked_bounds_with_stack_height(a: Collection[Interval]) -> Generator[Tuple[int, Linked_Bound, int], None, None]:
	"""
	Returns a generator yielding tuples;
	(
		stack_height_before:int
		bound:Linked_iBound
		stack_height_after:int
	)
	"""
	# TODO: remove dependence on linked bounds class?
	sorted_linked_bounds = sorted(itertools.chain.from_iterable(get_linked_bounds(a_interval) for a_interval in a))
	stack_count_before = 0
	stack_count_after = 0
	for previous_bound, current_bound, next_bound in util.iter_previous_current_next(sorted_linked_bounds):
		if current_bound.is_lower_bound:
			stack_count_after += 1
		else:
			stack_count_after -= 1
		yield stack_count_before, current_bound, stack_count_after
		stack_count_before = stack_count_after

	
def iter_bound_pairs(a: Collection[Interval]) -> Iterator[Tuple[Bound, Bound, bool]]:
	"""
	yields each pair of bounds in a collection of intervals where the bounds are obtained by get_sorted_linked_bounds_with_stack_height().
	Pairs of bounds that do not form a valid interval are ignored.
	If the first and last bounds are not infinite, these are added as required to make the output a complete traversal of the real number line.
	(
		previous_bound: iBound,
		next_bound: iBound,
		is_interior_interval: bool
	)
	"""
	INTERIOR = True
	EXTERIOR = False
	for ((_, prev_bound, _), (stack_before, bound, stack_after), (_, next_bound, _)) in util.iter_previous_current_next(get_sorted_linked_bounds_with_stack_height(a), (None, None, None)):
		if prev_bound is None:
			if bound != iBound_Negative_Infinity:
				yield iBound_Negative_Infinity, bound.bound, EXTERIOR
		else:
			if prev_bound.bound != bound.bound:
				yield prev_bound.bound, bound.bound, EXTERIOR if stack_before == 0 else INTERIOR
		
		if next_bound is None:
			if bound != iBound_Positive_Infinity:
				yield bound.bound, iBound_Positive_Infinity, EXTERIOR


def iter_bound_pairs_merge_touching(a: Collection[Interval]) -> Iterator[Tuple[Bound, Bound, bool]]:
	for is_interior, group in itertools.groupby(iter_bound_pairs(a), lambda item: item[2]):
		(first_bound, _, _), (_, last_bound, _) = util.first_and_last(group)
		yield first_bound, last_bound, is_interior


def coerce_collection_to_Interval_or_Multi_Interval(a: Collection[Interval]) -> Union[Interval, Multi_Interval]:
	if len(a) == 1:
		from .Interval import Interval
		if isinstance(a, Interval):
			return a
		else:
			#  This bit is needed because many _operators will return a list containing a single interval, which causes the isinstance test above to fail.
			return coerce_collection_to_Interval_or_Multi_Interval(*a)
	else:
		from .Multi_Interval import Multi_Interval
		if isinstance(a, Multi_Interval):
			return a
		else:
			return Multi_Interval(a)


def coerce_collection_to_Interval_or_None(a: Collection[Interval]) -> Optional[Interval]:
	if len(a) == 1:
		from .Interval import Interval
		if isinstance(a, Interval):
			return a
	return None


def eq_atomic(a: Interval, b: Interval):
	return a.lower_bound == b.lower_bound and a.upper_bound == b.upper_bound


def eq(a: Collection[Interval], b: Collection[Interval]) -> bool:
	b_intervals = list(b)
	if len(a) == len(b):
		try:
			for a_interval in a:
				index_of_first_atomic_match = next(index for index, b_interval in enumerate(b_intervals) if eq_atomic(a_interval, b_interval))
				b_intervals = b_intervals[:index_of_first_atomic_match] + b_intervals[index_of_first_atomic_match+1:]
		except ValueError:
			return False
		except StopIteration:
			return False
	else:
		return False
	return len(b_intervals) == 0


def union_merge_touching_OLD(a: Iterable[Interval], b: Iterable[Interval]):
	raise Exception("pretty sure this algorithim is wrong. switch to union_merge_on_predicate()")
	"""
		Adds each sub-interval of a to b and returns a new set of intervals.
		all sub-intervals from 'b' are added to the result as-is:
		then all sub-intervals from 'a' are added to the result one by one,
		as each sub-interval of 'a' is added it is merged with any intersecting or touching intervals already in the result using the hull operation.
		This means that if 'b' is a flattened multi interval, the result will also be a flat interval.
		"""
	result = tuple(b)
	for a_interval in a:
		new_result = []
		
		def split_condition(item: Interval):
			return touches_atomic(a_interval, item)
		
		for touching, r_intervals in itertools.groupby(sorted(result, key=split_condition), split_condition):
			if touching:
				# 'a_interval' touches all the 'r_intervals'. Add the hull to the result.
				new_result.extend(hull(itertools.chain(a_interval, r_intervals)))
			else:
				# 'a_interval' does not touch 'r_intervals'. Add both independently
				new_result.append(a_interval)
				new_result.extend(r_intervals)
		result = new_result
	return result


def union_merge_touching(a: Iterable[Interval], b: Iterable[Interval]):
	"""see union_merge_on_predicate for docs"""
	return union_merge_on_predicate(a, b, lambda a_sub, b_sub: touches_atomic(a_sub, b_sub))


def union_merge_intersecting_or_touching(a: Iterable[Interval], b: Iterable[Interval]):
	"""see union_merge_on_predicate for docs"""
	return union_merge_on_predicate(a, b, lambda a_sub, b_sub: intersects_atomic(a_sub, b_sub) or touches_atomic(a_sub, b_sub))


def union_merge_intersecting(a: Iterable[Interval], b: Iterable[Interval]):
	"""see union_merge_on_predicate for docs"""
	return union_merge_on_predicate(a, b, lambda a_sub, b_sub: intersects_atomic(a_sub, b_sub))


def union_merge_on_predicate(a: Iterable[Interval], b: Iterable[Interval], predicate: Callable[[Interval, Interval], bool]):
	"""
	Adds each sub-interval of b to a and returns a new set of intervals.
	all sub-intervals from 'a' are added to the result as-is:
	then all sub-intervals from 'b' are added to the result one by one,
	as each sub-interval of 'b' is added it is merged with any intervals already in the result for which the predicate returns true using the hull operation.
	This means that if 'a' is a flattened multi interval, the result will also be a flat interval.
	"""
	results = list(a)
	for item_to_insert in b:
		index = 0
		while index < len(results):
			result = results[index]
			if predicate(result, item_to_insert):
				item_to_insert = hull_atomic(item_to_insert, result)
				results.remove(result)
				index = 0
			index += 1
		results.append(item_to_insert)
	return results


def union_merge_intersecting_or_touching_linked(a: Iterable[Linked_Interval], b: Iterable[Linked_Interval]):
	"""see union_merge_on_predicate for docs"""
	return union_merge_on_predicate_linked(a, b, lambda a_sub, b_sub: intersects_atomic(a_sub, b_sub) or touches_atomic(a_sub, b_sub))


def union_merge_on_predicate_linked(a: Iterable[Linked_Interval], b: Iterable[Linked_Interval], predicate: Callable[[Interval, Interval], bool]) -> Collection[Linked_Interval]:
	"""
	Adds each sub-interval of b to a and returns a new set of intervals.
	all sub-intervals from 'a' are added to the result as-is:
	then all sub-intervals from 'b' are added to the result one by one,
	as each sub-interval of 'b' is added it is merged with any intervals already in the result for which the predicate returns true using the hull operation.
	This means that if 'a' is a flattened multi interval, the result will also be a flat interval.
	"""
	results = list(a)
	for item_to_insert in b:
		index = 0
		while index < len(results):
			result = results[index]
			if predicate(result, item_to_insert):
				item_to_insert = hull_atomic(item_to_insert, result).link_merge([*item_to_insert.linked_objects, *result.linked_objects])
				results.remove(result)
				index = 0
			index += 1
		results.append(item_to_insert)
	return results