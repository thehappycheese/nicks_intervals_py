from collections import deque
from itertools import chain
from itertools import islice
from itertools import tee
from typing import Any, TypeVar, Union, Optional, Callable, Iterable, Iterator, Tuple
import collections.abc

T = TypeVar("T")
K = TypeVar("K")


# credit to nosklo https://stackoverflow.com/questions/1011938/python-loop-that-also-accesses-previous-and-next-values
def iter_previous_current_next(some_iterable: Iterable[T], none_value: Optional[K] = None) -> Iterator[Tuple[Union[Optional[K], T], T, Union[Optional[K], T]]]:
	previous_items, current_items, next_items = tee(some_iterable, 3)
	previous_items = chain([none_value], previous_items)
	next_items = chain(islice(next_items, 1, None), [none_value])
	return zip(previous_items, current_items, next_items)


def iter_previous_current(some_iterable: Iterable[T], none_value: Optional[K] = None) -> Iterator[Tuple[Union[Optional[K], T], T]]:
	previous_items, current_items = tee(some_iterable, 2)
	previous_items = chain([none_value], previous_items)
	return zip(previous_items, current_items)


def iter_consecutive_disjoint_pairs(iterable: Iterable[T]) -> Iterator[Tuple[T, T]]:
	m = iterable if isinstance(iterable, collections.abc.Iterator) else iter(iterable)
	for a, b in zip(m, m):
		yield a, b
		
		
def iter_skip(iterable: Iterable[T], n) -> Iterator[T]:
	new_iterable = iterable if isinstance(iterable, collections.abc.Iterator) else iter(iterable)
	for _ in range(n):
		next(new_iterable)
	return new_iterable

# https://stackoverflow.com/questions/949098/python-split-a-list-based-on-a-condition/64979865#64979865
def iter_split_on_predicate(predicate: Callable[[T], bool], iterable: Iterable[T]) -> Tuple[Iterator[T], Iterator[T]]:
	new_iterable = iterable if isinstance(iterable, collections.abc.Iterator) else iter(iterable)
	hold_predicate_true = deque()
	hold_predicate_false = deque()
	
	def shared_generator():
		for item in new_iterable:
			print("Evaluate predicate.")
			if predicate(item):
				hold_predicate_true.appendleft(item)
				yield True
			else:
				hold_predicate_false.appendleft(item)
				yield False
	
	def iter_hold_queue_or_shared_generator(request, shared_gen, hold_queue):
		if not hold_queue:
			try:
				while next(shared_gen) != request:
					pass
			except:
				pass
		while hold_queue:
			print("Yield where predicate is "+str(request))
			yield hold_queue.pop()
			if not hold_queue:
				try:
					while next(shared_gen) != request:
						pass
				except:
					pass
			
	return iter_hold_queue_or_shared_generator(True, shared_generator(), hold_predicate_true), iter_hold_queue_or_shared_generator(False, shared_generator(), hold_predicate_false)



def first_and_last(iterable: Iterator) -> Tuple[Any, Any]:
	is_first = True
	last_item = None
	for item in iterable:
		if is_first:
			is_first = False
			yield item
		last_item = item
	yield last_item


# My recent dive into Haskell youtube videos is haunting my codebase:
# def iter_iBound_from_iter_Linked_iBound(iter_Linked_iBound:Iterable[Linked_iBound]) -> Iterator[iBound]:
# 	return (linked_bound.bound for linked_bound in iter_Linked_iBound)
#
#
# def iter_iBounds_with_infinities(iter_bounds: Iterable[iBound]) -> Iterator[Tuple[iBound, iBound, bool]]:
# 	""" returns an iterator yielding a tuple;
# 		(
# 			the last bound : iBound | None,
# 			the current bound : iBound,
# 			interior=True or exterior=False : bool
# 		)
# 	"""
# 	INTERIOR = True
# 	EXTERIOR = False
# 	previous_bound_and_current_bound_form_interior_interval = INTERIOR
# 	for previous_bound, bound, next_bound in iter_previous_and_next(iter_bounds):
# 		if previous_bound is None:
# 			if bound != iBound_Negative_Infinity:
# 				yield iBound_Negative_Infinity, bound, EXTERIOR
# 				previous_bound_and_current_bound_form_interior_interval = INTERIOR
# 			else:
# 				yield iBound_Negative_Infinity, bound, INTERIOR
# 				previous_bound_and_current_bound_form_interior_interval = EXTERIOR
# 		else:
# 			yield previous_bound, bound, previous_bound_and_current_bound_form_interior_interval
# 			previous_bound_and_current_bound_form_interior_interval = not previous_bound_and_current_bound_form_interior_interval
# 			if next_bound is None:
# 				if bound != iBound_Positive_Infinity:
# 					yield bound, iBound_Positive_Infinity, EXTERIOR
