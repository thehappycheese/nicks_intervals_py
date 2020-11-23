from __future__ import annotations

from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from NicksIntervals.iInterval import iInterval
import math


PART_OF_LEFT = True
PART_OF_RIGHT = False


class iBound:
	
	def __init__(self, value: float, part_of_left: bool):
		"""
		:param value: The floating point value of the bound.
		:param part_of_left: The direction of the bound. If True, this bound is part of the interval to the left of this bound (ie. if used as a lower bound, it means that the value of this bound is excluded from the interval; and if used as an upper bound it is included in the interval). If false, the opposite applies. It is recommended that the PART_OF_LEFT and PART_OF_RIGHT constants are imported from this module to make your code easier to read.
		"""
		try:
			float(value)
			self.__value = value
		except ValueError:
			raise TypeError("iBound(value={},...) parameter 'value' must be of type SupportsFloat")
		self.__part_of_left = part_of_left
		
		if not(isinstance(value, float) or isinstance(value, int)):
			raise TypeError(f"Unexpected argument type iBound(value: float|int,...) where value='{value}'")
		
		if not isinstance(part_of_left, bool):
			raise TypeError(f"Unexpected argument type iBound(...,part_of_left: bool) where part_of_left='{part_of_left}'")
		
		if self.__value == float("-inf") and self.part_of_left:
			raise Exception("Bounds at -inf must be included_in_right")
		
		elif self.__value == float("inf") and self.part_of_right:
			raise Exception("Bounds at inf must be included_in_left")
	
	def __eq__(self, other):
		if isinstance(other, iBound):
			return math.isclose(self.__value, other.__value) and self.__part_of_left == other.__part_of_left
		return NotImplemented
	
	def __gt__(self, other):
		if isinstance(other, (float, int)):
			raise Exception("should not be used")
			return self.__value > other
		elif isinstance(other, iBound):
			if math.isclose(self.__value, other.__value):
				return self.part_of_left and other.part_of_right
			else:
				return self.__value > other.__value
		
	def __lt__(self, other):
		if isinstance(other, (float, int)):
			raise Exception("should not be used")
			return self.__value < other
		elif isinstance(other, iBound):
			if math.isclose(self.__value, other.__value):
				return self.part_of_right and other.part_of_left
			else:
				return self.__value < other.__value
	
	def scaled(self, scale_factor: float) -> iBound:
		return iBound(self.__value*scale_factor, self.__part_of_left)
	
	def translated(self, translation: float) -> iBound:
		return iBound(self.__value + translation, self.__part_of_left)
	
	def translated_then_scaled(self, translation: float, scale_factor: float):
		return iBound((self.__value + translation) * scale_factor, self.__part_of_left)
	
	def scaled_then_translated(self, scale_factor: float, translation: float):
		return iBound(self.__value * scale_factor + translation, self.__part_of_left)
	
	@property
	def value(self):
		return self.__value
	
	@property
	def part_of_left(self) -> bool:
		"""The value of this bound part of the interval to the left"""
		return self.__part_of_left
	
	@property
	def part_of_right(self) -> bool:
		"""The value of this bound part of the interval to the right"""
		return not self.__part_of_left
	
	def inverted(self):
		return iBound(float(self), not self.__part_of_left)
	
	def __format__(self, format_spec):
		arrow = "🡆"
		if self.part_of_left:
			arrow = "🡄"
		return "iBound(" + ( f"{{:{format_spec}}}" ).format(self.__value) + "," + arrow + ")"
	
	def __repr__(self):
		return format(self, ".2f")
	
	def get_Linked_iBound(self, linked_interval: iInterval, is_lower_bound: bool):
		return Linked_iBound(self, linked_interval, is_lower_bound)


iBound_Negative_Infinity = iBound(float('-inf'), PART_OF_RIGHT)
iBound_Positive_Infinity = iBound(float('inf'), PART_OF_LEFT)


class Linked_iBound(iBound):
	def __init__(self, bound: iBound, interval: iInterval, is_lower_bound: bool):
		"""
		This class allows intervals to be decomposed into bounds without forgetting where the bound came from and if it was and an upper or lower bound.
		it should not be instantiated directly, but obtained through an instance of iInterval by calling:
		>>>iInterval(...).get_linked_bounds()
		"""
		super().__init__(bound.value, bound.part_of_left)
		self.__interval: iInterval = interval
		self.__bound: iBound = bound
		self.__is_lower_bound = is_lower_bound
	
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