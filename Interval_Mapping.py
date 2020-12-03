from __future__ import annotations

import itertools
from typing import Tuple, Collection, Iterable, Callable, Sequence

from NicksIntervals.Interval import Interval
import NicksIntervals._operators as ops
from NicksIntervals.Interval_Map import Interval_Map


class Interval_Mapping:
	def __init__(self, links: Iterable[Sequence[Interval, Interval]]):
		self.__links: Tuple[Interval_Map, ...] = tuple(Interval_Map(a, b) for a, b in links)
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
			self.__reversed = Interval_Mapping((b, a) for a, b in self.__links)
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
		return Interval_Mapping(result)