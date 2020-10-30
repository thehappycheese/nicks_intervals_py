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

from . import util



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
	
	def get_linked_bounds(self) -> Iterator[Linked_iBound]:
		return itertools.chain.from_iterable(interval.get_linked_bounds() for interval in self.__intervals)
	
	def get_sorted_linked_bounds_with_stack_height(self) -> Iterator[Tuple[int, Linked_iBound, int]]:
		"""
		Returns a generator yielding tuples;
		(
			stack_height_before:int
			bound:Linked_iBound
			stack_height_after:int
		)
		"""
		stack_count = 0
		for previous_bound, current_bound, next_bound in util.iter_previous_and_next(sorted(self.get_linked_bounds())):
			if current_bound.is_lower_bound:
				yield stack_count, current_bound, stack_count+1
				stack_count += 1
			else:
				stack_count -= 1
				yield stack_count+1, current_bound, stack_count
					
	def get_exterior_linked_bounds(self) -> Iterator[Linked_iBound]:
		# TODO: This function is wrong. we cant lose the stack count. iter_iBounds_with_infinities() assumes alternating interior exterior. only true if touching intervals are merged. this is probably necessary for exterior to work to avoid degenerate intervals, but merging touching is not strictly required to find the interior.
		#  anyway, we can circumvent the need for iter_iBounds_with_infinities by beefing up this function here to handle infinities.
		return (bound for stack_before, bound, stack_after in self.get_sorted_linked_bounds_with_stack_height() if stack_before == 0 or stack_after == 0)
	
	def flatten_ex_int(self):
		return [
			(lower_bound, upper_bound, "INTERIOR" if interior else "EXTERIOR")
			for lower_bound, upper_bound, interior
			in util.iter_iBounds_with_infinities(item[0] for item in itertools.groupby(util.iter_iBound_from_iter_Linked_iBound(self.get_exterior_linked_bounds())))
		]
	
	@property
	def exterior(self) -> iMulti_iInterval:
		return iMulti_iInterval(
			iInterval(lower_bound, upper_bound)
			for lower_bound, upper_bound, interior
			in util.iter_iBounds_with_infinities(item[0] for item in itertools.groupby(util.iter_iBound_from_iter_Linked_iBound(self.get_exterior_linked_bounds())))
			if not interior and not lower_bound == upper_bound
		)
		
	@property
	def interior(self) -> iMulti_iInterval:
		# assume for interior we may skip the itertools.groupby() step because none of the existing interior intervals would be an invalid degenerate??
		return iMulti_iInterval(
			iInterval(lower_bound, upper_bound)
			for lower_bound, upper_bound, interior
			in util.iter_iBounds_with_infinities(util.iter_iBound_from_iter_Linked_iBound(self.get_exterior_linked_bounds()))
			if interior and not lower_bound == upper_bound
		)
	
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