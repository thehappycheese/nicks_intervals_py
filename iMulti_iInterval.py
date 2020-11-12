from __future__ import annotations

import itertools
from typing import Generator
from typing import Iterable
from typing import Iterator
from typing import Tuple


import NicksIntervals.iInterval
from . import util
from .Linked_iBound import Linked_iBound
from .iBound import iBound
from .iBound import iBound_Negative_Infinity
from .iBound import iBound_Positive_Infinity
import NicksIntervals.non_atomic_super
import NicksIntervals._operators as ops


class iMulti_iInterval(NicksIntervals.non_atomic_super.non_atomic_super):

	def __init__(self, iter_intervals: Iterable[NicksIntervals.iInterval.iInterval]):
		self.__intervals: Tuple[NicksIntervals.iInterval.iInterval] = tuple(iter_intervals)
	
	@property
	def intervals(self) -> Iterable[NicksIntervals.iInterval.iInterval]:
		return self.__intervals
	
	def __iter__(self) -> Iterator[NicksIntervals.iInterval.iInterval]:
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
		return max(bound.bound for bound in itertools.chain.from_iterable(interval.get_linked_bounds() for interval in self.__intervals))
	
	@property
	def lower_bound(self) -> iBound:
		return min(bound.bound for bound in itertools.chain.from_iterable(interval.get_linked_bounds() for interval in self.__intervals))
	
	def get_sorted_linked_bounds_with_stack_height(self) -> Generator[Tuple[int, Linked_iBound, int], None, None]:
		"""
		Returns a generator yielding tuples;
		(
			stack_height_before:int
			bound:Linked_iBound
			stack_height_after:int
		)
		"""
		sorted_linked_bounds = sorted(itertools.chain.from_iterable(interval.get_linked_bounds() for interval in self.__intervals))
		stack_count_before = 0
		stack_count_after = 0
		for previous_bound, current_bound, next_bound in util.iter_previous_and_next(sorted_linked_bounds):
			if current_bound.is_lower_bound:
				stack_count_after += 1
			else:
				stack_count_after -= 1
			yield stack_count_before, current_bound, stack_count_after
			stack_count_before = stack_count_after
					
	def iter_bound_pairs(self) -> Iterator[Tuple[iBound, iBound, bool]]:
		"""
		iterates over each pair of bounds in all intervals returning a tuple
		pairs of bounds that do not form a valid interval are ignored.
		adds infinities to the exterior as required.
		(
			previous_bound: iBound,
			next_bound: iBound,
			is_interior_interval: bool
		)
		"""
		INTERIOR = True
		EXTERIOR = False
		for ((_, prev_bound, _), (stack_before, bound, stack_after), (_, next_bound, _)) in util.iter_previous_and_next(ops.get_sorted_linked_bounds_with_stack_height(self), (None, None, None)):
			if prev_bound is None:
				if bound != iBound_Negative_Infinity:
					yield iBound_Negative_Infinity, bound.bound, EXTERIOR
			else:
				if prev_bound.bound != bound.bound:
					yield prev_bound.bound, bound.bound, EXTERIOR if stack_before == 0 else INTERIOR
				
			if next_bound is None:
				if bound != iBound_Positive_Infinity:
					yield bound.bound, iBound_Positive_Infinity, EXTERIOR
	
	def iter_bound_pairs_merge_touching(self) -> Iterator[Tuple[iBound, iBound, bool]]:
		for is_interior, group in itertools.groupby(self.iter_bound_pairs(), lambda item: item[2]):
			(first_bound, _, _), (_, last_bound, _) = util.first_and_last(group)
			yield first_bound, last_bound, is_interior
	
	@property
	def exterior(self) -> iMulti_iInterval:
		return iMulti_iInterval(
			NicksIntervals.iInterval.iInterval(lower_bound, upper_bound)
			for lower_bound, upper_bound, interior
			in self.iter_bound_pairs()
			if not interior
		)
		
	@property
	def interior(self) -> iMulti_iInterval:
		return iMulti_iInterval(
			NicksIntervals.iInterval.iInterval(lower_bound, upper_bound)
			for lower_bound, upper_bound, interior
			in self.iter_bound_pairs()
			if interior
		)
	
	@property
	def interior_merged(self) -> iMulti_iInterval:
		return iMulti_iInterval(
			NicksIntervals.iInterval.iInterval(lower_bound, upper_bound)
			for lower_bound, upper_bound, interior
			in self.iter_bound_pairs_merge_touching()
			if interior
		)
	
	def without_infinitesimal(self) -> iMulti_iInterval:
		return iMulti_iInterval(interval for interval in self.__intervals if not interval.is_infinitesimal)
	
	def has_infinitesimal(self):
		return any(interval.is_infinitesimal for interval in self.__intervals)  # I learned generator expressions :O
