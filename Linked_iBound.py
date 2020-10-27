from __future__ import annotations

import math

from NicksIntervals.iBound import iBound
from NicksIntervals.iBound import iBound
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from NicksIntervals.iInterval import iInterval


class Linked_iBound(iBound):
	def __init__(self, interval: iInterval, bound: iBound):
		"""
		This class allows intervals to be decomposed into bounds without forgetting where the bound came from and if it was and an upper or lower bound.
		it should not be instantiated directly, but obtained through an instance of iInterval by calling:
		>>>iInterval(...).get_connected_bounds()
		"""
		super().__init__(bound.value, bound.part_of_left)
		self.__interval: iInterval = interval
		self.__bound: iBound = bound
		self.__is_lower_bound: bool
		if interval.lower_bound is bound:
			self.__is_lower_bound = True
		elif interval.upper_bound is bound:
			self.__is_lower_bound = False
		else:
			raise Exception("bound must be part of the interval")
	
	def __format__(self, format_spec):
		lower_or_upper_bound_string = "Lower"
		if self.is_upper_bound:
			lower_or_upper_bound_string = "Upper"
		return f"Linked_{super().__format__(format_spec)[:-1]},{lower_or_upper_bound_string})"
	
	def __gt__(self, other):
		if isinstance(other, Linked_iBound):
			if math.isclose(self.value, other.value) and self.part_of_left == other.part_of_left:
				return self.is_lower_bound and other.is_upper_bound
		return super().__gt__(other)

	def __lt__(self, other):
		if isinstance(other, Linked_iBound):
			if math.isclose(self.value, other.value) and self.part_of_left == other.part_of_left:
				return self.is_upper_bound and other.is_lower_bound
		return super().__lt__(other)
	
	@property
	def interval(self):
		"""a reference back to the interval which created this connected_iBound"""
		return self.__interval
	
	@property
	def bound(self):
		"""a reference back to the original immutable iBound object which the interval uses"""
		return self.__bound
	
	@property
	def is_lower_bound(self):
		return self.__is_lower_bound
	
	@property
	def is_upper_bound(self):
		return not self.__is_lower_bound
