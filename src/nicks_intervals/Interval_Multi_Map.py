from __future__ import annotations

import itertools
from typing import Tuple, Iterable, Callable, Sequence

from .Interval import Interval
from . import _operators as ops
from .Interval_Map import Interval_Map


class Interval_Multi_Map:
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
			self.__reversed = Interval_Multi_Map((b, a) for a, b in self.__links)
		return self.__reversed
		
	def map_intervals(self, intervals: Iterable[Interval]):
		return ops.coerce_collection_to_Interval_or_Multi_Interval(
			ops.apply_interval_maps_to_intervals(self.__links, intervals)
		)
	
	def unmap_intervals(self):
		raise Exception("to be implemented if required")
	
	def map_value(self, value: float) -> Sequence[float]:
		return ops.apply_interval_maps_to_value(self.__links, value)
	
	def map_value_nearest(self, value: float):
		"""Same as map_value(), but first ensures that the input value is inside the nearest interval."""
		return self.map_value(ops.nearest_contained_value(self.get_from(), value))[0]
		
	def unmap_value(self):
		raise Exception("to be implemented if required")
	
	@classmethod
	def predicate_always(cls, *args):
		return True
	
	@classmethod
	def predicate_never(cls, *args):
		return True
	
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
		All combinations are tested, and the process starts again each time a merge is performed."""
		# TODO: this is a very slow algorithm O(n^2) or O(n!) ? not good stuff. We can improve by creating an 'add and merge'
		# TODO: this algorithm has issues when one interval_map completely contains the other.
		#  Might be better to progressively build the map using .add_merge_if_contained_or_touching()
		
		result = [*self.__links]
		must_restart = True
		while must_restart:
			must_restart = False
			for a, b in itertools.combinations(result, 2):
				if from_predicate(a[0], b[0]) and to_predicate(a[1], b[1]):
					result.remove(a)
					result.remove(b)
					result.append((
						ops.hull_atomic(a[0], b[0]),
						ops.hull_atomic(a[1], b[1])
					))
					must_restart = True
					break
		return Interval_Multi_Map(result)
	
	def add_merge_if_contained_or_touching(self, interval_map_to_add: Interval_Map) -> Interval_Multi_Map:
		"""Returns a new Interval_Multi_Map with an additional element.
		If the new element touches any existing element (on both dimensions)
		it will be merged, and the check for touching will restart.
		If the new element is contained within any existing element then no change is made.
		If any existing element is contained within the new element, it is removed before the new element is added.
		"""
		
		interval_map_to_add = [interval_map_to_add]

		result = list(self.__links)
		
		must_restart = True
		
		while must_restart:
			must_restart = False
			for sub_result in result:
				if sub_result.contains(interval_map_to_add[0]):
					interval_map_to_add = []
					break
				elif interval_map_to_add[0].contains(sub_result):
					result.remove(sub_result)
					must_restart = True
					break
				elif sub_result.touches(interval_map_to_add[0]):
					interval_map_to_add = [interval_map_to_add[0].merge_by_hull(sub_result)]
					result.remove(sub_result)
					must_restart = True
					break
					
		return Interval_Multi_Map([*result, *interval_map_to_add])