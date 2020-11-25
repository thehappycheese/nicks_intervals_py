from __future__ import annotations

import itertools
from typing import Tuple, Collection, Iterable, Callable

from NicksIntervals import util
from NicksIntervals.iInterval import iInterval
import NicksIntervals._operators as ops


class iInterval_Map:
	def __init__(self, links: Iterable[Tuple[iInterval, iInterval]]):
		self.__links = tuple(links)
		self.__reversed = None
	
	def get_from(self):
		return iInterval.coerce_from_collection([item[0] for item in self.__links])
	
	def get_to(self):
		return iInterval.coerce_from_collection([item[1] for item in self.__links])
	
	@property
	def links(self):
		return self.__links
	
	def reverse(self):
		if self.__reversed is None:
			self.__reversed = iInterval_Map((b, a) for a, b in self.__links)
		return self.__reversed
		
	def map_intervals(self, intervals: Iterable[iInterval]):
		return ops.coerce_iInterval_collection(
			ops.apply_interval_maps_to_intervals(self.__links, intervals)
		)
	
	def unmap_intervals(self):
		raise Exception("to be implemented if required")
	
	def map_value(self, values: float) -> Collection[float]:
		return ops.apply_interval_maps_to_value(self.__links, values)
	
	def unmap_value(self):
		raise Exception("to be implemented if required")
	
	@classmethod
	def predicate_touching(cls, a: iInterval, b: iInterval):
		return ops.touches_atomic(a, b)
	
	@classmethod
	def predicate_touching_or_intersecting(cls, a: iInterval, b: iInterval):
		return ops.touches_atomic(a, b) or ops.intersects_atomic(a, b)
	
	@classmethod
	def predicate_intersecting(cls, a: iInterval, b: iInterval):
		return ops.intersects_atomic(a, b)
	
	def merge_on_predicates(self, from_predicate: Callable[[iInterval, iInterval], bool], to_predicate: Callable[[iInterval, iInterval], bool]):
		"""Merge links based on the provided predicates; the iInterval_Map class provide some helpers as @classmethods.
		All combinations are tested, and the process starts again each time a merge is performed.
		TODO: this is a very slow algorithm O(n^2) or O(n!) ? not good stuff"""
		
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
		return iInterval_Map(result)