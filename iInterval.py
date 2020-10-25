"""
Nicholas Archer
2020-10-08

Roads are made of segments, and I nearly exploded with frustration writing code to work with overlapping or touching intervals.
Also I am using this to process midi files.
"""

from __future__ import annotations

import itertools
import math
from typing import Iterable
from typing import Tuple
from typing import Union

from .iBound import PART_OF_LEFT
from .iBound import PART_OF_RIGHT
from .iBound import iBound
from .iBound import iBound_Negative_Infinity
from .iBound import iBound_Positive_Infinity
from .iMulti_iInterval import iMulti_iInterval


class iInterval:
	"""Immutable Interval based on python's built in floats. Nothing fancy."""
	
	@classmethod
	def complete(cls):
		return iInterval(
			lower_bound=iBound_Positive_Infinity,
			upper_bound=iBound_Negative_Infinity
		)
	
	@classmethod
	def degenerate(cls, value: float = 0.0):
		return iInterval(
			lower_bound=iBound(value, PART_OF_RIGHT),
			upper_bound=iBound(value, PART_OF_LEFT)
		)
	
	@classmethod
	def closed(cls, lower_bound: float, upper_bound: float):
		return iInterval(iBound(lower_bound, PART_OF_RIGHT), iBound(upper_bound, PART_OF_LEFT))
	
	@classmethod
	def open(cls, lower_bound: float, upper_bound: float):
		return iInterval(iBound(lower_bound, PART_OF_LEFT), iBound(upper_bound, PART_OF_RIGHT))
	
	@classmethod
	def open_closed(cls, lower_bound: float, upper_bound: float):
		return iInterval(iBound(lower_bound, PART_OF_LEFT), iBound(upper_bound, PART_OF_LEFT))
	
	@classmethod
	def closed_open(cls, lower_bound: float, upper_bound: float):
		return iInterval(iBound(lower_bound, PART_OF_RIGHT), iBound(upper_bound, PART_OF_RIGHT))
	
	def __init__(self, lower_bound: iBound, upper_bound: iBound):
		try:
			assert isinstance(lower_bound, iBound)
			assert isinstance(upper_bound, iBound)
		except AssertionError:
			raise TypeError("Bounds must be an instance of iBound")
		
		self.__lower_bound: iBound = lower_bound
		self.__upper_bound: iBound = upper_bound
		
		self.__is_infinitesimal: bool = False
		self.__is_degenerate: bool = False
		self.__is_complete = lower_bound.value == float('-inf') and upper_bound.value == float('inf')
		
		if lower_bound.value == upper_bound.value:
			if self.__lower_bound.part_of_right and self.__upper_bound.part_of_left:
				self.__is_degenerate = True
			else:
				raise Exception(f"Degenerate intervals (lower_bound==upper_bound) are only permitted when both bounds are closed.")
		elif math.isclose(lower_bound.value, upper_bound.value):
			self.__is_infinitesimal = True
			# TODO: emit warning? infinitesimal intervals will cause havoc with other algorithms
			#  im really on the fence about this one. i think i need to do more research about precision models
			#  ima raise an exception here until i have a better idea.
			raise Exception(f"Infinitesimal intervals are not cool: {lower_bound} <= {upper_bound} == {lower_bound<=upper_bound}")
		elif lower_bound.value > upper_bound.value:
			raise Exception(f"reversed intervals are not permitted. lower_bound.value must be less than or equal to upper_bound.value: {lower_bound} <= {upper_bound} == {lower_bound.value<=upper_bound.value}")
		
		
		
	def __format__(self, format_spec):
		char_left = f"{format(float(self.__lower_bound.value), format_spec)}"
		char_right = f"{format(float(self.__upper_bound.value), format_spec)}"
		
		if self.__lower_bound == iBound_Negative_Infinity:
			char_left = "-∞"
		
		if self.__upper_bound == iBound_Positive_Infinity:
			char_right = "+∞"
		
		if self.__lower_bound.part_of_right:
			char_left = "≤"+char_left  # ≤ [
		else:
			char_left = "<" + char_left  # < (
		
		if self.__upper_bound.part_of_left:
			char_right = char_right+"≥"  # ≥ ]
		else:
			char_right = char_right+">"  # > )
		return f"{char_left}, {char_right}"
		
	def __repr__(self):
		return format(self, ".3f")
	
	def __iter__(self):
		return iter((self,))
	
	def print(self):
		"""
		prints intervals and multi intervals like this for debugging (only works for integer intervals):
		╠═════╣
			╠═════╣    ╞═══╣
		"""
		out = f"{self:2.0f} :"
		for i in range(0, int(min(50, round(self.__upper_bound.value))) + 1):
			if i < round(self.__lower_bound.value):
				out += " "
			elif round(self.__lower_bound.value) == i == round(self.__upper_bound.value):
				out += "║"
			elif i == round(self.__lower_bound.value):
				if self.__lower_bound.part_of_right:
					out += "╠"
				else:
					out += "╞"
			elif i == round(self.__upper_bound.value):
				if self.__upper_bound.part_of_left:
					out += "╣"
				else:
					out += "╡"
			else:
				out += "═"
		print(out)
		return self
	
	@property
	def lower_bound(self) -> iBound:
		return self.__lower_bound
	
	@property
	def upper_bound(self) -> iBound:
		return self.__upper_bound
	
	@property
	def is_degenerate(self) -> bool:
		return self.__is_degenerate
	
	@property
	def is_infinitesimal(self) -> bool:
		return self.__is_infinitesimal
	
	@property
	def is_complete(self) -> bool:
		return self.__is_complete
	
	@ property
	def length(self) -> float:
		return self.__upper_bound.value - self.__lower_bound.value
	
	def interpolate(self, ratio: float) -> float:
		return self.__lower_bound.value + (self.__upper_bound.value - self.__lower_bound.value) * ratio
	
	def contains_value(self, value: float) -> bool:
		if self.__is_degenerate:
			return math.isclose(self.__lower_bound.value, value)
		else:
			if math.isclose(self.__lower_bound.value, value) and self.__lower_bound.part_of_right:
				return True
			elif math.isclose(self.__upper_bound.value, value) and self.__upper_bound.part_of_left:
				return True
			elif self.__lower_bound < value < self.__upper_bound:
				return True
		return False
	
	def contains_upper_bound(self, bound: iBound) -> bool:
		if self.__is_degenerate and math.isclose(self.__lower_bound.value, bound.value):
			return bound.part_of_left
		else:
			if math.isclose(self.__lower_bound.value, bound.value):
				return self.__lower_bound.part_of_right and bound.part_of_left
			if math.isclose(self.__upper_bound.value, bound.value):
				return not (self.__upper_bound.part_of_right and bound.part_of_left)
			elif self.__lower_bound < bound < self.__upper_bound:
				return True
		return False
	
	def contains_lower_bound(self, bound: iBound) -> bool:
		if self.__is_degenerate and math.isclose(self.__upper_bound.value, bound.value):
			return bound.part_of_right
		else:
			if math.isclose(self.__lower_bound.value, bound.value):
				return not (self.__lower_bound.part_of_left and bound.part_of_right)
			if math.isclose(self.__upper_bound.value, bound.value):
				return self.__upper_bound.part_of_left and bound.part_of_right
			if self.__lower_bound < bound < self.__upper_bound:
				return True
		return False
		
	def contains_interval(self, other: iInterval) -> bool:
		if self.__is_degenerate and other.__is_degenerate and math.isclose(self.__lower_bound.value, other.__lower_bound.value):
			return True
		else:
			return self.contains_lower_bound(other.__lower_bound) and self.contains_upper_bound(other.__upper_bound)
	
	@property
	def left_exterior(self) -> Tuple[iInterval, ...]:
		if self.__lower_bound == iBound_Negative_Infinity:
			return tuple()
		else:
			return (iInterval(iBound_Negative_Infinity, self.__lower_bound), )
	
	@property
	def right_exterior(self) -> Union[Tuple[()], Tuple[iInterval]]:
		if self.__upper_bound == iBound_Positive_Infinity:
			return tuple()
		else:
			return (iInterval(self.__upper_bound, iBound_Positive_Infinity), )
		
	@property
	def exterior(self) -> Union[Tuple[()], Tuple[iInterval], Tuple[iInterval, iInterval]]:
		return (*self.left_exterior, *self.right_exterior)
	
	def touches(self, other: Iterable[iInterval]) -> bool:
		for other_interval in other:
			if math.isclose(self.__lower_bound.value, other_interval.__upper_bound.value) and (self.__lower_bound.part_of_right == other_interval.__upper_bound.part_of_right):
				return True
			if math.isclose(self.__upper_bound.value, other_interval.__lower_bound.value) and (self.__upper_bound.part_of_left == other_interval.__lower_bound.part_of_left):
				return True
		return False
	
	def intersects(self, other: Iterable[iInterval]) -> bool:
		for other_interval in other:
			if (
				self.contains_lower_bound(other_interval.__lower_bound) or
				self.contains_upper_bound(other_interval.__upper_bound) or
				other_interval.contains_lower_bound(self.__lower_bound) or
				other_interval.contains_upper_bound(self.__upper_bound)
			):
				return True
		return False
	
	def intersect(self, other: Iterable[iInterval]) -> Iterable[iInterval]:
		result = []
		for other_interval in other:
			self_contains_other_lower_bound = self.contains_lower_bound(other_interval.__lower_bound)
			self_contains_other_upper_bound = self.contains_upper_bound(other_interval.__upper_bound)
			
			#   self:  ╠════════════╣
			#  other:        ╠════╣
			# result:        ╠════╣
			if self_contains_other_lower_bound and self_contains_other_upper_bound:
				result.extend(other_interval)
			
			other_contains_self_lower_bound = other_interval.contains_lower_bound(self.__lower_bound)
			
			#   self:        ╠══════════╣
			#  other:  ╠════════════╣
			# result:        ╠══════╣
			if other_contains_self_lower_bound:
				result.extend(iInterval(self.__lower_bound, other_interval.__upper_bound))
			
			other_contains_self_upper_bound = other_interval.contains_upper_bound(self.__upper_bound)
			
			#   self:        ╠════╣
			#  other:  ╠════════════╣
			# result:        ╠════╣
			if other_contains_self_lower_bound and other_contains_self_upper_bound:
				result.extend(self)
				
			#   self:    ╠══════════╣
			#  other:        ╠════════════╣
			# result:        ╠══════╣
			if other_contains_self_upper_bound:
				result.extend(iInterval(other_interval.__lower_bound, self.__upper_bound))
		return tuple(result)
	
	def subtract(self, other: Iterable[iInterval]) -> Iterable[iInterval]:
		
		# TODO: This works. But can it be even more slick...
		# result = self
		# for other_sub_interval in other:
		# 	p1 = []
		# 	for self_sub_interval in result:
		# 		p1.extend(itertools.chain(*(exterior.intersect(self_sub_interval) for exterior in other_sub_interval.exterior)))
		# 	result = tuple(p1)
		# return result
		
		result = self
		for other_sub_interval in other:
			result = (
				itertools.chain(*(
					itertools.chain(*(
						exterior.intersect(self_sub_interval) for exterior in other_sub_interval.exterior
					)) for self_sub_interval in result
				))
			)
		return tuple(result)
	
	def hull(self, other: Iterable[iInterval]) -> Iterable[iInterval]:
		result_lower_bound = self.__lower_bound
		result_upper_bound = self.__upper_bound
		for other_interval in other:
			if other_interval.__lower_bound < result_lower_bound:
				result_lower_bound = other_interval.__lower_bound
			if other_interval.__lower_bound > result_upper_bound:
				result_upper_bound = other_interval.__upper_bound
		return iInterval(result_lower_bound, result_upper_bound)
	
	def union(self, other: Iterable[iInterval]) -> Iterable[iInterval]:
		return tuple(itertools.chain(self, other))
