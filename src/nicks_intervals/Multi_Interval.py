from __future__ import annotations

import itertools
from typing import Iterable, Collection, TYPE_CHECKING, Optional

from . import Interval
# if TYPE_CHECKING:
from . import Bound


class Multi_Interval(Interval.Interval):
	
	def __init__(self, iter_intervals: Iterable[Interval.Interval]):
		self.__intervals: Collection[Interval.Interval] = tuple(iter_intervals)
	
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
	def upper_bound(self) -> Optional[Bound.Bound]:
		# raise Exception("Should not be called internally")
		if len(self.__intervals) > 0:
			return max(bound.bound for bound in itertools.chain.from_iterable(interval.get_linked_bounds() for interval in self.__intervals))
		else:
			return None
	
	@property
	def lower_bound(self) -> Optional[Bound.Bound]:
		# raise Exception("Should not be called internally")
		if len(self.__intervals) > 0:
			return min(bound.bound for bound in itertools.chain.from_iterable(interval.get_linked_bounds() for interval in self.__intervals))
		else:
			return None
		
	def interior_merged(self):
		return Interval.ops.coerce_collection_to_Interval_or_Multi_Interval(Interval.ops.interior_merged(self))
