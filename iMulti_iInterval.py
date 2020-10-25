from __future__ import annotations

import itertools
from typing import Iterable
from typing import Iterator
from typing import List
from typing import TYPE_CHECKING
from typing import Tuple
from typing import Union

from .iBound import iBound
from .iBound import iBound_Negative_Infinity
from .iBound import iBound_Positive_Infinity
from .iInterval import iInterval
#if TYPE_CHECKING:
from .iInterval import Linked_iBound




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
	
	def get_exterior_connected_bounds(self) -> List[Linked_iBound]:
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
	
	def get_exterior_bounds(self) -> List[iBound]:
		stack_count = 0
		item: Linked_iBound
		out = []
		for item in sorted(itertools.chain(*(interval.get_connected_bounds() for interval in self.__intervals))):
			if item.is_lower_bound:
				if stack_count == 0:
					out.append(item.bound)
				stack_count += 1
			else:
				stack_count -= 1
				if stack_count == 0:
					out.append(item.bound)
		return out
	
	@property
	def exterior(self) -> Iterable[iInterval]:
		eb = self.get_exterior_bounds()
		if eb[0] != iBound_Negative_Infinity:
			eb = [iBound_Negative_Infinity]+eb
		if eb[-1] != iBound_Positive_Infinity:
			eb = eb+[iBound_Positive_Infinity]
		return tuple(iInterval(a, b) for a, b in zip(*([iter(eb)]*2)))
		
	
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
		
	def add_overlapping(self, interval: Union[iInterval, iMulti_iInterval]) -> iMulti_iInterval:
		"""Add to multi interval without further processing. Overlapping intervals will be preserved.
		this is similar to doing: MultiInterval().intervals.append(Interval()) except it also works on Multi_Intervals
		:return: self
		"""
		if isinstance(interval, iInterval):
			self.__intervals.append(interval)
		elif isinstance(interval, iMulti_iInterval):
			self.__intervals.extend(item for item in interval.intervals)
		else:
			raise TypeError(f"Could not add_overlapping item ({interval}) of type {type(interval).__qualname__}")
		return self
	
	def add_hard(self, interval_to_add: iInterval) -> Multi_Interval:
		"""Add to multi interval, truncating or deleting existing intervals to prevent overlaps with the new interval
		will result in touching intervals being maintained
		may result in infinitesimal interval being added
		:return: self
		"""
		# TODO: Make multi interval compatible
		self.subtract(interval_to_add)
		self.add_overlapping(interval_to_add)
		return self
	
	def add_soft(self, interval_to_add: Interval) -> Multi_Interval:
		"""Add Interval() to Multi_Interval(), truncating or ignoring the new interval to prevent overlaps with existing intervals
		will result in touching intervals being maintained
		may result in infinitesimal interval being added
		:return: self
		"""
		# TODO: Make multi interval compatible
		for interval in self.__intervals:
			if interval.intersects(interval_to_add):
				interval_to_add = interval_to_add.subtract(interval)
				if interval_to_add is None:
					break
		
		if isinstance(interval_to_add, Multi_Interval):
			for sub_interval in interval_to_add.__intervals:
				self.__intervals.append(sub_interval.copy())
		elif isinstance(interval_to_add, Interval):
			self.add_overlapping(interval_to_add)
		elif interval_to_add is None:
			pass
		else:
			raise Exception("add soft failed")
		
		return self
	
	def add_merge(self, interval_to_add: Interval) -> Multi_Interval:
		"""Add Interval() to Multi_Interval(), merge with any overlapping or touching intervals to prevent overlaps
		preserves existing intervals that are touching, only merges existing intervals which touch or intersect with the new interval
		:return: self
		"""
		# TODO: Make multi interval compatible
		
		original_interval_to_add = interval_to_add
		
		must_restart = True
		while must_restart:
			must_restart = False
			for interval in self.__intervals:
				if interval.intersects(original_interval_to_add) or interval.touches(original_interval_to_add):
					interval_to_add = interval_to_add.hull(interval)
					self.__intervals.remove(interval)
					must_restart = True
					break
		self.__intervals.append(interval_to_add)
		return self
	
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