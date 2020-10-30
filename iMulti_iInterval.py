from __future__ import annotations

import itertools
from typing import Iterable
from typing import Iterator
from typing import Tuple
from typing import Union

from .iBound import iBound
from .iBound import iBound_Negative_Infinity
from .iBound import iBound_Positive_Infinity

from .iInterval import iInterval
from .Linked_iBound import Linked_iBound

from itertools import chain, islice, tee


# credit to nosklo https://stackoverflow.com/questions/1011938/python-loop-that-also-accesses-previous-and-next-values
def previous_and_next(some_iterable):
	previous_items, current_items, next_items = tee(some_iterable, 3)
	previous_items = chain([None], previous_items)
	next_items = chain(islice(next_items, 1, None), [None])
	return zip(previous_items, current_items, next_items)


def with_infinities(iter_bounds: Iterable[iBound]) -> Iterable[Tuple[iBound, bool]]:
	""" returns an iterator yielding a tuple;
		(
			the last bound : iBound | None,
			the current bound : iBound,
			interior=True or exterior=False : bool
		)
	"""
	INTERIOR = True
	EXTERIOR = False
	current_state = INTERIOR
	for previous_bound, bound, next_bound in previous_and_next(iter_bounds):
		if previous_bound is None:
			if bound != iBound_Negative_Infinity:
				yield iBound_Negative_Infinity, bound, EXTERIOR
				current_state = INTERIOR
			else:
				yield iBound_Negative_Infinity, bound, INTERIOR
				current_state = EXTERIOR
		if next_bound is None:
			if bound != iBound_Positive_Infinity:
				yield bound, iBound_Positive_Infinity, EXTERIOR
			else:
				yield bound, iBound_Positive_Infinity, INTERIOR
		else:
			yield previous_bound, bound, current_state
			current_state = not current_state
	

def without_duplicated_bounds(iter_bounds: Iterable[iBound]):
	"""
	Eliminates interior duplicate bounds
	"""

	for previous_bound, bound, next_bound in previous_and_next(iter_bounds):
		if previous_bound is None:
			yield bound
		elif next_bound is None:
			yield bound
		else:
		
		


class iMulti_iInterval:
	def __init__(self, iter_intervals: Iterable[iInterval]):
		self.__lower_bound: iBound = iBound_Positive_Infinity
		self.__upper_bound: iBound = iBound_Negative_Infinity
		self.__intervals: Tuple[iInterval] = tuple(sorted(iter_intervals, key=lambda item: item.lower_bound))
		self.__is_empty = False
		if len(self.__intervals) == 0:
			self.__is_empty = True
		else:
			for interval in self.__intervals:
				if interval.lower_bound < self.__lower_bound:
					self.__lower_bound = interval.lower_bound
				if interval.upper_bound > self.__upper_bound:
					self.__upper_bound = interval.upper_bound
		
	@property
	def is_empty(self):
		return self.__is_empty
	
	@property
	def intervals(self) -> Iterable[iInterval]:
		return self.__intervals
	
	def __iter__(self) -> Iterator[iInterval]:
		return iter(self.__intervals)
	
	def __format__(self, format_spec):
		return f"Multi_Interval[{len(self.__intervals)}]([{', '.join(['...' + str(len(self.__intervals)) if index == 4 else format(interval, format_spec) for index, interval in enumerate(self.__intervals) if index < 5])}])"
	
	def __repr__(self):
		return self.__format__(".2f")
	
	 
	
	def print(self):
		print("Multi_Interval:")
		for sub_interval in self.__intervals:
			sub_interval.print()
		print("")
		return self
	
	def __bool__(self):
		return bool(self.__intervals)
	
	@property
	def upper_bound(self) -> iBound:
		return self.__upper_bound
	
	@property
	def lower_bound(self) -> iBound:
		return self.__lower_bound
	
	def get_exterior_linked_bounds(self) -> Iterable[Linked_iBound]:
		stack_count = 0
		item: Linked_iBound
		out = []
		for item in sorted(itertools.chain(*(interval.get_connected_bounds() for interval in self.__intervals))):
			if item.is_lower_bound:
				if stack_count == 0:
					out.append(item)
				stack_count += 1
			else:
				stack_count -= 1
				if stack_count == 0:
					out.append(item)
		return out
	
	def get_exterior_bounds(self) -> Iterable[iBound]:
		return [linked_bound.bound for linked_bound in self.get_exterior_linked_bounds()]
	
	@property
	def exterior(self) -> Iterable[iInterval]:
		return tuple(iInterval(lower_bound, upper_bound) for lower_bound, upper_bound , interior in zip(*([with_infinities(self.get_exterior_bounds())]*2)) if not interior)  # TODO: wrong if starts at neg inf
		
	@property
	def interior(self):
		exterior_bounds = self.get_exterior_bounds()
		return tuple(iInterval(a, b) for a, b in zip(*([iter(exterior_bounds)] * 2)) if a != b)
	
	def subtract(self, interval_to_subtract: iInterval):
		new_interval_list = []
		for interval in self:
			if interval.intersects(interval_to_subtract):  # TODO: not great efficiency
				f = interval.subtract(interval_to_subtract)
				if f is not None:
					try:
						# assume f is a Multi_Interval
						for pieces in f.__intervals:
							new_interval_list.append(pieces)
					except:
						# f is an Interval
						new_interval_list.append(f)
			else:
				new_interval_list.append(interval)
		return iMulti_iInterval(new_interval_list)
		
	def intersection(self, arg_interval: Union[Interval, Multi_Interval]) -> Multi_Interval:
		if isinstance(arg_interval, Multi_Interval):
			result_multi_interval: Multi_Interval = type(self)([])
			for my_interval in self.__intervals:
				for other_interval in arg_interval.__intervals:
					result_multi_interval.add_soft(my_interval.intersect(other_interval))
			return result_multi_interval.delete_infinitesimal()
		elif isinstance(arg_interval, Interval):
			result_multi_interval: Multi_Interval = type(self)([])
			for my_interval in self.__intervals:
				result_multi_interval.add_soft(my_interval.intersect(arg_interval))
			return result_multi_interval.delete_infinitesimal()
		else:
			raise Exception("Type error in MultiInterval().intersection()")
	
	def merge_touching_and_intersecting(self) -> Multi_iInterval:
		"""
		:return: eliminates all touching or intersecting intervals by merging
		"""
		must_restart = True
		while must_restart:
			must_restart = False
			for a, b in itertools.combinations(self.__intervals, 2):
				if a.intersects(b) or a.touches(b):
					c = a.hull(b)
					self.__intervals.remove(a)
					self.__intervals.remove(b)
					self.__intervals.append(c)
					must_restart = True
					break
		return self
	
	def delete_infinitesimal(self) -> Multi_iInterval:
		self.__intervals = [interval for interval in self.__intervals if not interval.is_infinitesimal]
		return self
	
	def has_infinitesimal(self):
		return any(interval.is_infinitesimal for interval in self.__intervals)  # I learned generator expressions :O
	
	def hull(self) -> iInterval:
		if self.__intervals:
			return iInterval(self.lower_bound, self.upper_bound)
		else:
			return None