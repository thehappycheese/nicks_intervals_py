from __future__ import annotations

from typing import Iterable, Collection

import NicksIntervals.iInterval


class iMulti_iInterval(NicksIntervals.iInterval.iInterval):

	def __init__(self, iter_intervals: Iterable[NicksIntervals.iInterval.iInterval]):
		self.__intervals: Collection[NicksIntervals.iInterval.iInterval] = tuple(iter_intervals)
	
	def __format__(self, format_spec):
		return f"Multi_Interval[{len(self.__intervals)}]([{', '.join(['...' + str(len(self.__intervals)) if index == 4 else format(interval, format_spec) for index, interval in enumerate(self.__intervals) if index < 5])}])"
	
	def __iter__(self):
		return iter(self.__intervals)
	
	def __len__(self):
		return len(self.__intervals)
	
	def __bool__(self):
		return bool(self.__intervals)
	
	def __contains__(self, item):
		return item in self.__intervals
		
	def print(self):
		print("Multi_Interval:")
		for sub_interval in self.__intervals:
			sub_interval.print()
		print("")
		return self
	
	@property
	def upper_bound(self) -> NicksIntervals.iBound.iBound:
		raise Exception("Should not be called internally")
		return max(bound.bound for bound in itertools.chain.from_iterable(interval.get_linked_bounds() for interval in self.__intervals))
	
	@property
	def lower_bound(self) -> NicksIntervals.iBound.iBound:
		raise Exception("Should not be called internally")
		return min(bound.bound for bound in itertools.chain.from_iterable(interval.get_linked_bounds() for interval in self.__intervals))
