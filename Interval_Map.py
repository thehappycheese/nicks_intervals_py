from __future__ import annotations

import itertools
from typing import Tuple, Collection, Iterable, Callable, Sequence

from NicksIntervals.Interval import Interval
import NicksIntervals._operators as ops


class Interval_Link:
	
	def __init__(self, interval_in_dimension_a: Interval, interval_in_dimension_b: Interval):
		"""Used to form an Interval_Map."""
		# TODO: hold info about degenerate cases; if the from space is degenerate, then how will the to space behave?
		#  this is currently determined by the _operators.
		self.__interval_a = interval_in_dimension_a
		self.__interval_b = interval_in_dimension_b
		
	def __len__(self):
		return 2
	
	def __getitem__(self, item: int):
		if item == 0:
			return self.__interval_a
		elif item == 1:
			return self.__interval_b
		raise IndexError(f"{self.__class__.__qualname__} has only 2 index-able items, [0], and [1]. Negative indices are not supported")
	
	def __iter__(self):
		return iter((self.__interval_a, self.__interval_b))
	
	def __reversed__(self):
		return Interval_Link(self.__interval_b, self.__interval_a)
	
	def __contains__(self, item):
		return (item is self.__interval_a) or (item is self.__interval_b)
	
	def contains(self, interval_link: Interval_Link):
		return self.__interval_a.contains_interval(interval_link.__interval_a) and self.__interval_b.contains_interval(interval_link.__interval_b)
	
	def touches(self, interval_link: Interval_Link):
		return self.__interval_a.touches(interval_link.__interval_a) and self.__interval_b.touches(interval_link.__interval_b)
	
	def merge(self, interval_link: Interval_Link):
		a = ops.coerce_collection_to_Interval_or_None(self.__interval_a.hull(interval_link.__interval_a))
		b = ops.coerce_collection_to_Interval_or_None(self.__interval_b.hull(interval_link.__interval_b))
		if a and b:
			return Interval_Link(a, b)
		return None
	
	@property
	def from_dimension(self) -> Interval:
		return self.__interval_a
	
	@property
	def to_dimension(self) -> Interval:
		return self.__interval_b


class Interval_Map:
	def __init__(self, links: Iterable[Sequence[Interval, Interval]]):
		self.__links: Tuple[Interval_Link, ...] = tuple(Interval_Link(a, b) for a, b in links)
		self.__reversed = None
	
	def get_from(self):
		return Interval.coerce_collection_to_Interval_or_Multi_Interval([item[0] for item in self.__links])
	
	def get_to(self):
		return Interval.coerce_collection_to_Interval_or_Multi_Interval([item[1] for item in self.__links])
	
	@property
	def links(self):
		return self.__links
	
	def reverse(self):
		if self.__reversed is None:
			self.__reversed = Interval_Map((b, a) for a, b in self.__links)
		return self.__reversed
		
	def map_intervals(self, intervals: Iterable[Interval]):
		return ops.coerce_collection_to_Interval_or_Multi_Interval(
			ops.apply_interval_maps_to_intervals(self.__links, intervals)
		)
	
	def unmap_intervals(self):
		raise Exception("to be implemented if required")
	
	def map_value(self, values: float) -> Collection[float]:
		return ops.apply_interval_maps_to_value(self.__links, values)
	
	def unmap_value(self):
		raise Exception("to be implemented if required")
	
	@classmethod
	def predicate_touching(cls, a: Interval, b: Interval):
		return ops.touches_atomic(a, b)
	
	@classmethod
	def predicate_touching_or_intersecting(cls, a: Interval, b: Interval):
		return ops.touches_atomic(a, b) or ops.intersects_atomic(a, b)
	
	@classmethod
	def predicate_intersecting(cls, a: Interval, b: Interval):
		return ops.intersects_atomic(a, b)
	
	def merge_on_predicates(self, from_predicate: Callable[[Interval, Interval], bool], to_predicate: Callable[[Interval, Interval], bool]):
		"""Merge links based on the provided predicates; the Interval_Map class provide some helpers as @classmethods.
		All combinations are tested, and the process starts again each time a merge is performed.
		TODO: this is a very slow algorithm O(n^2) or O(n!) ? not good stuff. We can improve by creating an 'add and merge'"""
		
		result = [*self.__links]
		restart = True
		while restart:
			restart = False
			for a, b in itertools.combinations(result, 2):
				if from_predicate(a[0], b[0]) and to_predicate(a[1], b[1]):
					result.remove(a)
					result.remove(b)
					result.append((
						ops.hull_atomic(a[0], b[0]),
						ops.hull_atomic(a[1], b[1])
					))
					restart = True
					break
		return Interval_Map(result)