"""
Nicholas Archer
2020-10-08

Roads are made of segments, and I nearly exploded with frustration writing code to work with overlapping or touching intervals.
Also I am using this to process midi files.
"""

from __future__ import annotations

import math
from typing import List
from typing import Union

Infinity = float('inf')


class iInterval:
	"""Immutable Interval based on python's built in floats. Nothing fancy."""
	
	@classmethod
	def complete(cls):
		return iInterval(
			lower_bound=-Infinity,
			upper_bound=Infinity,
			lower_bound_closed=True,
			upper_bound_closed=True
		)
	
	@classmethod
	def degenerate(cls, at: float = 0.0):
		return iInterval(
			lower_bound=at,
			upper_bound=at,
			lower_bound_closed=False,
			upper_bound_closed=False
		)
		
	def __init__(self, lower_bound: float, upper_bound: float, lower_bound_closed: bool = True, upper_bound_closed: bool = True):
		# runtime type-checks to catch sneaky errors
		try:
			assert(isinstance(lower_bound, float) or isinstance(lower_bound, int))
			assert(isinstance(upper_bound, float) or isinstance(upper_bound, int))
			assert(isinstance(lower_bound_closed, bool))
			assert(isinstance(upper_bound_closed, bool))
		except AssertionError as e:
			raise TypeError(f"Type of argument(s) incorrect:  {self.__class__.__qualname__}({lower_bound}: float, {upper_bound}: float, {lower_bound_closed}: bool, {upper_bound_closed}: bool)")
		
		self.__is_infinitesimal:bool = False
		self.__is_degenerate:bool = False
		self.__lower_bound:float = float(lower_bound)
		self.__upper_bound:float = float(upper_bound)
		self.__lower_bound_closed:bool = bool(lower_bound_closed)
		self.__upper_bound_closed:bool = bool(upper_bound_closed)
		
		if lower_bound == upper_bound:
			if self.__lower_bound_closed and self.__upper_bound_closed:
				self.__is_degenerate = True
			else:
				raise Exception(f"Degenerate intervals (lower_bound==upper_bound) are only permitted when both bounds are closed.")
		elif math.isclose(lower_bound, upper_bound):
			self.__is_infinitesimal = True
		elif lower_bound > upper_bound:
			raise Exception(f"reversed intervals are not permitted. lower_bound must be less than or equal to upper_bound: {lower_bound}<={upper_bound} == {lower_bound<=upper_bound}")
	
	def __format__(self, format_spec):
		char_left = f"{format(self.__lower_bound, format_spec)}"
		char_right = f"{format(self.__upper_bound, format_spec)}"
		
		if self.__lower_bound == -Infinity:
			char_left = "-∞"
		
		if self.__upper_bound == Infinity:
			char_right = "+∞"
		
		if self.__lower_bound_closed:
			char_left = "◀ "+char_left
		else:
			char_left = "◁ " + char_left
		
		if self.__upper_bound_closed:
			char_right = char_right+" ▶"
		else:
			char_right = char_right+" ▷"
		return f"{char_left} {char_right}"
		
	def __repr__(self):
		return format(self, ".2f")
	
	def print(self):
		"""
		prints intervals and multi intervals like this for debugging (only works for integer intervals):
		   ├─────┤
			├──────┤    ├────┤
		"""
		if self.__lower_bound < 0 or self.__upper_bound > 100:
			return "error cant print"
		out = f"{self:.2f} :"
		for i in range(int(self.end) + 1):
			if i < self.start:
				out += " "
			elif self.start == i == self.end:
				out += "║"
			elif i == self.start:
				if self.__lower_bound_closed:
					out += "╠"
				else:
					out += "╞"
			elif i == self.end:
				if self.__upper_bound_closed:
					out += "╣"
				else:
					out += "╡"
			else:
				out += "═"
		print(out)
	
	@property
	def start(self) -> float:
		return self.__lower_bound
	
	@property
	def end(self) -> float:
		return self.__upper_bound
	
	@property
	def lower_bound(self) -> float:
		return self.__lower_bound
	
	@property
	def upper_bound(self) -> float:
		return self.__upper_bound
	
	@property
	def lower_bound_closed(self) -> bool:
		return self.__lower_bound_closed
	
	@property
	def upper_bound_closed(self) -> bool:
		return self.__upper_bound_closed
	
	@property
	def is_degenerate(self) -> bool:
		return self.__is_degenerate
	
	@property
	def is_infinitesimal(self) -> bool:
		return self.__is_infinitesimal
	
	@ property
	def length(self):
		return self.__upper_bound - self.__lower_bound
	
	def left_exterior(self):
		if self.__lower_bound == -Infinity:
			if self.__lower_bound_closed:
				return None
			else:
				return iInterval.degenerate(-Infinity)
		else:
			return iInterval(-Infinity, self.__lower_bound, lower_bound_closed=not self.__lower_bound_closed)
	
	def right_exterior(self):
		if self.__upper_bound == Infinity:
			if self.__upper_bound_closed:
				return None
			else:
				return iInterval.degenerate(Infinity)
		else:
			return iInterval(self.__upper_bound, Infinity, upper_bound_closed=not self.__upper_bound_closed)
	
	def interpolate(self, ratio: float):
		return self.__lower_bound + (self.__upper_bound - self.__lower_bound) * ratio
	
	def contains_value(self, value: float):
		if self.__is_degenerate:
			return math.isclose(self.__lower_bound, value)
		else:
			if self.__lower_bound < value < self.__upper_bound:
				return True
			elif self.__lower_bound_closed and math.isclose(value, self.__lower_bound):
				return True
			elif self.__upper_bound_closed and math.isclose(value, self.__upper_bound):
				return True
		return False
	
	def contains_value_as_if_self_closed(self, value):
		""" returns the same as contains_value but behaves as if self.__lower_bound_closed == True and self.__upper_bound_closed == True
		"""
		if self.__is_degenerate:
			return math.isclose(self.__lower_bound, value)
		else:
			if self.__lower_bound < value < self.__upper_bound:
				return True
			elif math.isclose(value, self.__lower_bound):
				return True
			elif math.isclose(value, self.__upper_bound):
				return True
		return False
	
	def contains_interval(self, other: iInterval):
		if self.__is_degenerate and other.__is_degenerate and math.isclose(self.__lower_bound, other.__lower_bound):
			return True
		else:
			self_contains_other_lower_bound = self.contains_value(other.__lower_bound) or (other.__lower_bound_closed==False and self.__lower_bound)
			self_contains_other_upper_bound = self.contains_value(other.__upper_bound)
			
			raise Exception("bed time")
			
			if not self_contains_other_lower_bound:
				if not self.__lower_bound_closed and other.__lower_bound_closed
			
			if self_contains_other_lower_bound and self_contains_other_upper_bound:
				return True
			elif other.__lower_bound
			
	
	def exterior(self) -> Union[None, iInterval, List[iInterval]]:
		left_exterior = self.left_exterior()
		right_exterior = self.right_exterior()
		if left_exterior is None and right_exterior is None:
			return None
		elif left_exterior is None:
			return right_exterior
		elif right_exterior is None:
			return left_exterior
		else:
			return [left_exterior, right_exterior]
	
	def intersect(self, other: iInterval) -> Union[iInterval, List[iInterval], None]:
		if not isinstance(other, iInterval):
			raise Exception('iInterval may only be intersected with iInterval at this time.')
		
		self_contains_other_lower_bound = self.contains_value(other.__lower_bound)
		self_contains_other_upper_bound = self.contains_value(other.__upper_bound)
		other_contains_self_lower_bound = other.contains_value(self.__lower_bound)
		other_contains_self_upper_bound = other.contains_value(self.__upper_bound)
		
		# To the left of other
		#  self:  ╠════╣
		# other:        ╠════╣
		if self.end < other.start:
			if self_contains_other_lower_bound:
				# Touching outside
				#  self:  ╠════╣
				# other:       ╠════╣
				return iInterval.degenerate(at=self.__upper_bound_closed)
			else:
				# Disjoint
				#  self:  ╠════╣
				# other:       ╞════╣
				return None
		
		# To the right of other:
		#  self:         ╠════╣
		# other:  ╠════╣
		if self.start > other.end:
			if self_contains_other_upper_bound:
				# Touching Outside
				#  self:       ╠════╣
				# other:  ╠════╣
				return iInterval.degenerate(at=self.__lower_bound)
			else:
				# Disjoint
				#  self:       ╠════╣
				# other:  ╠════╡
				return None
		
		# if self.end >= other.start and self.start <= other.end
		#  self: ╠════╣
		# other:    ╠════╣
		#            or
		#  self:    ╠════╣
		# other: ╠════╣
		if self.start > other.end:
			if self_contains_other_upper_bound:
				# Touching Outside
				#  self:       ╠════╣
				# other:  ╠════╣
				return iInterval.degenerate(at=self.__lower_bound)
			else:
				# Disjoint
				#  self:       ╠════╣
				# other:  ╠════╡
				return None
		
		#  |---|
		#    |---|
		if other_contains_self_upper_bound and not other_contains_self_lower_bound:
			return iInterval(other.__lower_bound, self.__upper_bound, other.__upper_bound_closed, self.__upper_bound_closed)
			
		#    |-|
		#    |---|
		if other_contains_self_upper_bound and not other_contains_self_lower_bound:
			return iInterval(other.__lower_bound, self.__upper_bound, other.__upper_bound_closed, self.__upper_bound_closed)
		
		if self.start <= other.start:  # accepts equality; in the case of zero length intersections both return statements below are equivalent
			#  |---|
			#    |---|
			if self.end < other.end:
				return type(self)(other.start, self.end)
			
			#  |-------|
			#    |---|
			return type(self)(other.start, other.end)
		
		if self.start <= other.end:
			#    |---|
			#  |-------|
			if self.end < other.end:
				return type(self)(self.start, self.end)
			
			#    |---|
			#  |---|
			return type(self)(self.start, other.end)