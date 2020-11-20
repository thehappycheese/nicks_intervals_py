from __future__ import annotations
from typing import Tuple, Collection, Iterable

from NicksIntervals.iInterval import iInterval
import NicksIntervals._operators as ops

class iInterval_Map:
	def __init__(self, links: Iterable[Tuple[iInterval, iInterval]]):
		self.__links = tuple(links)
		
	def reverse(self):
		return iInterval_Map((b, a) for a, b in self.__links)
	
	def map(self, intervals: Iterable[iInterval]) -> Collection[iInterval]:
		return ops.coerce_iInterval_collection(
			ops.apply_interval_maps(self.__links, intervals)
		)