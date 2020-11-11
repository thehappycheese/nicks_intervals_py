from __future__ import annotations
import NicksIntervals.Linked_iBound
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
			self.__value = float(value)
		except ValueError:
			raise TypeError("iBound(value={},...) parameter 'value' must be of type SupportsFloat")
		self.__part_of_left = part_of_left
		
		if not(isinstance(value, float) or isinstance(value, int)):
			raise TypeError(f"Unexpected argument type iBound(value=float,...) where value='{value}'")
		
		if not isinstance(part_of_left, bool):
			raise TypeError(f"Unexpected argument type iBound(...,part_of_left=bool) where part_of_left='{part_of_left}'")
		
		if self == float("-inf") and self.part_of_left:
			raise Exception("Bounds at -inf must be included_in_right")
		
		elif self == float("inf") and self.part_of_right:
			raise Exception("Bounds at inf must be included_in_left")
	
	def __eq__(self, other):
		if isinstance(other, (float, int)):
			return self.__value == other
		elif isinstance(other, iBound):
			return math.isclose(self.__value, other.__value) and self.__part_of_left == other.__part_of_left
	
	def __gt__(self, other):
		if isinstance(other, (float, int)):
			return self.__value > other
		elif isinstance(other, iBound):
			if math.isclose(self.__value, other.__value):
				return self.part_of_left and other.part_of_right
			else:
				return self.__value > other.__value
		
	def __lt__(self, other):
		if isinstance(other, (float, int)):
			return self.__value < other
		elif isinstance(other, iBound):
			if math.isclose(self.__value, other.__value):
				return self.part_of_right and other.part_of_left
			else:
				return self.__value < other.__value
	
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
		return NicksIntervals.Linked_iBound.Linked_iBound(self, linked_interval, is_lower_bound)


iBound_Negative_Infinity = iBound(float('-inf'), PART_OF_RIGHT)
iBound_Positive_Infinity = iBound(float('inf'), PART_OF_LEFT)
