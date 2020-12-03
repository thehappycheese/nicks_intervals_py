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
	"""[1,2,3,4,5] -> ( (None,1,2), (1,2,3), (2,3,4), (3,4,5), (4,5,None) )"""
	previous_items, current_items, next_items = tee(some_iterable, 3)
	previous_items = chain([none_value], previous_items)
	next_items = chain(islice(next_items, 1, None), [none_value])
	return zip(previous_items, current_items, next_items)


def iter_previous_current(some_iterable: Iterable[T], none_value: Optional[K] = None) -> Iterator[Tuple[Union[Optional[K], T], T]]:
	"""[1,2,3,4,5] -> ( (None,1), (1,2), (2,3), (3,4), (4,5) )"""
	previous_items, current_items = tee(some_iterable, 2)
	previous_items = chain([none_value], previous_items)
	return zip(previous_items, current_items)


def iter_consecutive_disjoint_pairs(iterable: Iterable[T]) -> Iterator[Tuple[T, T]]:
	"""[1,2,3,4,5] -> ( (1,2), (3,4) )"""
	m = iterable if isinstance(iterable, collections.abc.Iterator) else iter(iterable)
	for a, b in zip(m, m):
		yield a, b


def iter_consecutive_overlapping_pairs(iterable: Iterable[T]) -> Iterator[Tuple[T, T]]:
	"""[1,2,3,4,5] -> ( (1,2), (2,3), (3,4), (4,5) )"""
	m, p = tee(iterable)
	next(p)
	for a, b in zip(m, p):
		yield a, b
		
		
def iter_skip(n, iterable: Iterable[T]) -> Iterator[T]:
	new_iterable = iterable if isinstance(iterable, collections.abc.Iterator) else iter(iterable)
	for _ in range(n):
		next(new_iterable)
	return new_iterable


# https://stackoverflow.com/questions/949098/python-split-a-list-based-on-a-condition/64979865#64979865
def iter_split_on_predicate(predicate: Callable[[T], bool], iterable: Iterable[T]) -> Tuple[Iterator[T], Iterator[T]]:
	deque_predicate_true = deque()
	deque_predicate_false = deque()
	
	# define a generator function to consume the input iterable
	# the Predicate is evaluated once per item, added to the appropriate deque, and the predicate result it yielded
	def shared_generator(definitely_an_iterator):
		for item in definitely_an_iterator:
			print("Evaluate predicate.")
			if predicate(item):
				deque_predicate_true.appendleft(item)
				yield True
			else:
				deque_predicate_false.appendleft(item)
				yield False
	
	# consume input iterable only once,
	# converting to an iterator with the iter() function if necessary. Probably this conversion is unnecessary
	shared_gen = shared_generator(
		iterable if isinstance(iterable, collections.abc.Iterator) else iter(iterable)
	)
	
	# define a generator function for each predicate outcome and queue
	def iter_for(predicate_value, hold_queue):
		def consume_shared_generator_until_hold_queue_contains_something():
			if not hold_queue:
				try:
					while next(shared_gen) != predicate_value:
						pass
				except:
					pass
		
		consume_shared_generator_until_hold_queue_contains_something()
		while hold_queue:
			print("Yield where predicate is "+str(predicate_value))
			yield hold_queue.pop()
			consume_shared_generator_until_hold_queue_contains_something()
	
	# return a tuple of two generators
	return iter_for(predicate_value=True, hold_queue=deque_predicate_true), iter_for(predicate_value=False, hold_queue=deque_predicate_false)


def first_and_last(iterable: Iterator) -> Tuple[Any, Any]:
	is_first = True
	last_item = None
	for item in iterable:
		if is_first:
			is_first = False
			yield item
		last_item = item
	yield last_item