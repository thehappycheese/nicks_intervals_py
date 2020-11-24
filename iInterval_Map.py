from __future__ import annotations

import itertools
from typing import Tuple, Collection, Iterable

from NicksIntervals import util
from NicksIntervals.iInterval import iInterval
import NicksIntervals._operators as ops


class iInterval_Map:
	def __init__(self, links: Iterable[Tuple[iInterval, iInterval]]):
		self.__links = tuple(links)
		self.__reversed = None
	
	@property
	def links(self):
		return self.__links
	
	def reverse(self):
		if self.__reversed is None:
			self.__reversed = iInterval_Map((b, a) for a, b in self.__links)
		return self.__reversed
		
	def map_interval(self, intervals: Iterable[iInterval]):
		return ops.coerce_iInterval_collection(
			ops.apply_interval_maps_to_intervals(self.__links, intervals)
		)
	
	def unmap_interval(self):
		raise Exception("to be implemented if required")
	
	def map_values(self, values: Iterable[float]) -> Collection[float]:
		return ops.apply_interval_maps_to_values(self.__links, values)
	
	def unmap_values(self):
		raise Exception("to be implemented if required")
	
	def merge_touching(self):
		raise Exception("deso not work??")
		"""if both the input and output interval are touching an adjacent interval, merge them."""
		# TODO: this is a very slow algorithm O(n^2), O(n!), not good stuff
		result = [*self.__links]
		restart = True
		while restart:
			restart = False
			for a, b in util.iter_skip(1, util.iter_previous_current(result)):
				if ops.touches_atomic(a[0], b[0]) and ops.touches_atomic(a[1], b[1]):
					result.remove(a)
					result.remove(b)
					result.append((
						ops.hull_atomic(a[0], b[0]),
						ops.hull_atomic(a[1], b[1])
					))
					restart = True
					break
		return iInterval_Map(result)