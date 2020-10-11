"""
Nicholas Archer
2020-10-08

Roads are made of segments, and I nearly exploded with frustration writing code to work with overlapping or touching intervals.
Also I am using this to process midi files.
"""

from __future__ import annotations

import math
import itertools
from typing import Iterable
from typing import List
from typing import Tuple
from typing import Union

from .iBound import iBound
from .iMulti_iInterval import iMulti_iInterval

Infinity = float('inf')


def resolve_iterable_of_iInterval_to_type(intervals: Union[List[iInterval], Tuple[iInterval]]) -> Union[None, iInterval, iMulti_iInterval]:
	if len(intervals) == 0:
		return None
	elif len(intervals) == 1:
		return intervals[0]
	else:
		return iMulti_iInterval(intervals)


class iInterval:
	"""Immutable Interval based on python's built in floats. Nothing fancy."""
	
	@classmethod
	def complete(cls):
		# TODO: there may be issues with comparison to the instance returned by this method.
		#  Do we expect all complete intervals to be equivalent to this object
		#  >>> some_iInterval is iInterval.complete())
		#  or be equal to the value of this object by overriding the __eq__?
		#  >>> some_iInterval == iInterval.complete()
		return iInterval(
			lower_bound=-Infinity,
			upper_bound=Infinity,
			lower_bound_closed=True,
			upper_bound_closed=True
		)
	
	@classmethod
	def degenerate(cls, at: float = 0.0):
		# TODO: i am not sure these are needed in practice. If they can be eliminated that would be good.
		#  Degenerate intervals are the same as a float.
		#  They are not like a iBound which must be interpreted as upper or lower to truly make comparisons with them.
		#  They are a double closed bound and are useless.
		#  in writing this comment, I am now wondering if iBounds should have a __closed_left and __closed_right property.
		#  this might  allow us to crunch down some of the algorithms here.
		#  bound could implement a 'contains' function to simplify some of the nightmarish math.isclose() logic in iInterval.
		
		# TODO:write some tests to see if it actually works.
		return iInterval(
			lower_bound=at,
			upper_bound=at,
			lower_bound_closed=True,
			upper_bound_closed=True
		)
	
	def __init__(self, lower_bound: Union[float, iBound], upper_bound: Union[float, iBound], lower_bound_closed: bool = None, upper_bound_closed: bool = None):
		"""
		
		:param lower_bound: either provide a float or an iBound. if a float is provided is converted internally. If a bound is provided its .closed property is used and lower_bound_closed must be None
		:param upper_bound: ''
		:param lower_bound_closed: bool (None by default which results in True)
		:param upper_bound_closed: bool (None by default which results in True)
		"""
		if isinstance(lower_bound, iBound):
			if lower_bound_closed is not None:
				raise Exception("If iBounds are used in place of floats, then lower_bound_closed argument should not be provided")
		elif isinstance(lower_bound, float) or isinstance(lower_bound, int):
			if lower_bound_closed is None:
				lower_bound_closed = True
			if not isinstance(lower_bound_closed, bool):
				raise TypeError("lower_bound_closed must be bool when lower bound is float.")
			lower_bound = iBound(lower_bound, lower_bound_closed)
		else:
			raise TypeError("lower_bound mut be float or iBound")
		
		if isinstance(upper_bound, iBound):
			if upper_bound_closed is not None:
				raise Exception("If iBounds are used in place of floats, then upper_bound_closed argument should not be provided")
		elif isinstance(upper_bound, float) or isinstance(upper_bound, int):
			if upper_bound_closed is None:
				upper_bound_closed = True
			upper_bound = iBound(upper_bound, upper_bound_closed)
		else:
			raise TypeError("Lower bound incorrect type")
		
		self.__lower_bound: iBound = lower_bound
		self.__upper_bound: iBound = upper_bound
		
		self.__is_infinitesimal: bool = False
		self.__is_degenerate: bool = False
		
		if lower_bound == upper_bound:
			if self.__lower_bound.closed and self.__upper_bound.closed:
				self.__is_degenerate = True
			else:
				raise Exception(f"Degenerate intervals (lower_bound==upper_bound) are only permitted when both bounds are closed.")
		elif math.isclose(lower_bound, upper_bound):
			self.__is_infinitesimal = True
			# TODO: emit warning? infinitesimal intervals will cause havoc with other algorithms
			#  im really on the fence about this one. i think i need to do more research about precision models
			#  ima raise an exception here until i have a better idea.
		elif lower_bound > upper_bound:
			raise Exception(f"reversed intervals are not permitted. lower_bound must be less than or equal to upper_bound: {lower_bound}<={upper_bound} == {lower_bound<=upper_bound}")
	
	def __format__(self, format_spec):
		char_left = f"{format(self.__lower_bound, format_spec)}"
		char_right = f"{format(self.__upper_bound, format_spec)}"
		
		if self.__lower_bound == -Infinity:
			char_left = "-∞"
		
		if self.__upper_bound == Infinity:
			char_right = "+∞"
		
		if self.__lower_bound.closed:
			char_left = "≤"+char_left  # ≤ [
		else:
			char_left = "<" + char_left  # < (
		
		if self.__upper_bound.closed:
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
		for i in range(0, int(min(50, round(self.__upper_bound))) + 1):
			if i < round(self.__lower_bound):
				out += " "
			elif round(self.__lower_bound) == i == round(self.__upper_bound):
				out += "║"
			elif i == round(self.__lower_bound):
				if self.__lower_bound.closed:
					out += "╠"
				else:
					out += "╞"
			elif i == round(self.__upper_bound):
				if self.__upper_bound.closed:
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
	def lower_bound_closed(self) -> bool:
		return self.__lower_bound.closed
	
	@property
	def upper_bound_closed(self) -> bool:
		return self.__upper_bound.closed
	
	@property
	def is_degenerate(self) -> bool:
		return self.__is_degenerate
	
	@property
	def is_infinitesimal(self) -> bool:
		return self.__is_infinitesimal
	
	@ property
	def length(self) -> float:
		return self.__upper_bound - self.__lower_bound
	
	def interpolate(self, ratio: float) -> float:
		return self.__lower_bound + (self.__upper_bound - self.__lower_bound) * ratio
	
	def contains_value(self, value: float) -> bool:
		if self.__is_degenerate:
			return math.isclose(self.__lower_bound, value)
		else:
			if self.__lower_bound < value < self.__upper_bound:
				return True
			elif self.__lower_bound.closed and math.isclose(value, self.__lower_bound):
				return True
			elif self.__upper_bound.closed and math.isclose(value, self.__upper_bound):
				return True
		return False
	
	def contains_upper_bound(self, bound: iBound) -> bool:
		if self.__is_degenerate and math.isclose(self.__lower_bound, bound):
			return True
		else:
			if self.__upper_bound.open and bound.open and math.isclose(self.__upper_bound, bound):
				return True
			if bound.open and math.isclose(self.__lower_bound, bound):
				return False
			if self.contains_value(bound):
				return True
		return False
	
	def contains_lower_bound(self, bound: iBound) -> bool:
		if self.__is_degenerate and math.isclose(self.__upper_bound, bound):
			return True
		else:
			if self.__lower_bound.open and bound.open and math.isclose(self.__lower_bound, bound):
				return True
			if bound.open and math.isclose(self.__upper_bound, bound):
				return False
			if self.contains_value(bound):
				return True
		return False
		
	def contains_interval(self, other: iInterval) -> bool:
		if self.__is_degenerate and other.__is_degenerate and math.isclose(self.__lower_bound, other.__lower_bound):
			return True
		else:
			return self.contains_lower_bound(other.__lower_bound) and self.contains_upper_bound(other.__upper_bound)
	
	@property
	def left_exterior(self) -> List[iInterval]:
		if self.__lower_bound == -Infinity:
			if self.__lower_bound.closed:
				return []
			else:
				return [iInterval.degenerate(-Infinity)]
		else:
			return [iInterval(-Infinity, iBound(self.__lower_bound, not self.__lower_bound.closed))]
	
	@property
	def right_exterior(self) -> iInterval:
		if self.__upper_bound == Infinity:
			if self.__upper_bound.closed:
				return []
			else:
				return [iInterval.degenerate(Infinity)]
		else:
			return [iInterval(iBound(self.__upper_bound, not self.__upper_bound.closed), Infinity)]
		
	@property
	def exterior(self) -> iMulti_iInterval:
		return iMulti_iInterval((*self.left_exterior, *self.right_exterior))
	
	def intersects(self, other: Union[iInterval, iMulti_iInterval]) -> bool:
		for other_interval in other:
			if (
				self.contains_lower_bound(other_interval.__lower_bound) or
				self.contains_upper_bound(other_interval.__upper_bound) or
				other.contains_lower_bound(self.__lower_bound) or
				other.contains_upper_bound(self.__upper_bound)
			):
				return True
		return False
	
	def intersect(self, other: Union[iInterval, iMulti_iInterval]):
		result = []
		for other_interval in other:
			self_contains_other_lower_bound = self.contains_lower_bound(other_interval.__lower_bound)
			self_contains_other_upper_bound = self.contains_upper_bound(other_interval.__upper_bound)
			
			#   self:  ╠════════════╣
			#  other:        ╠════╣
			# result:        ╠════╣
			if self_contains_other_lower_bound and self_contains_other_upper_bound:
				result.extend(other_interval)
			
			other_contains_self_lower_bound = other.contains_lower_bound(self.__lower_bound)
			
			#   self:        ╠══════════╣
			#  other:  ╠════════════╣
			# result:        ╠══════╣
			if other_contains_self_lower_bound:
				result.extend(iInterval(self.__lower_bound, other.__upper_bound))
			
			other_contains_self_upper_bound = other.contains_upper_bound(self.__upper_bound)
			
			#   self:        ╠════╣
			#  other:  ╠════════════╣
			# result:        ╠════╣
			if other_contains_self_lower_bound and other_contains_self_upper_bound:
				result.extend(self)
				
			#   self:    ╠══════════╣
			#  other:        ╠════════════╣
			# result:        ╠══════╣
			if other_contains_self_upper_bound:
				result.extend(iInterval(other.__lower_bound, self.__upper_bound))
		return resolve_iterable_of_iInterval_to_type(result)
	
	def subtract(self, other: Union[iInterval, iMulti_iInterval]):
		result = (item for item in itertools.chain(*[exterior.intersect(self) for exterior in other.exterior]))
		return resolve_iterable_of_iInterval_to_type((*result,))
	
	def hull(self, other: Union[iInterval, iMulti_iInterval]) -> iInterval:
		
		lowest_most_closed_bound = self.__lower_bound
		if math.isclose(other.lower_bound, self.__lower_bound):
			if other.lower_bound.closed and self.__lower_bound.open:
				lowest_most_closed_bound = other.lower_bound
		elif other.lower_bound < self.__lower_bound:
			lowest_most_closed_bound = other.lower_bound
		else:
			pass  # already correct
		
		highest_most_closed_bound = self.__upper_bound
		if math.isclose(other.upper_bound, self.__upper_bound):
			if other.upper_bound.closed and self.__upper_bound.open:
				highest_most_closed_bound = other.upper_bound
		elif other.upper_bound > self.__upper_bound:
			highest_most_closed_bound = other.upper_bound
		else:
			pass  # already correct
		
		return iInterval(lowest_most_closed_bound, highest_most_closed_bound)
	
	def union(self, other: Union[iInterval, iMulti_iInterval]):
		# th union of an overlapping multi-interval is ... wierd
		resolve_iterable_of_iInterval_to_type((self, *other))