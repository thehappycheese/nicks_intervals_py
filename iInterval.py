"""
Nicholas Archer
2020/06/09

Roads are made of segments, and I nearly exploded with frustration writing code to work with overlapping or touching intervals.
"""

from __future__ import annotations

import itertools
import math
from typing import Iterable, Union, List, Any


Infinity = float('inf')

class iBound (float):
	def __init__(self, value: float, open_bound: bool = False):
		if not isinstance(value, float):
			raise TypeError("iBound(value=...) must be float")
		if not isinstance(open_bound, bool):
			raise TypeError("iBound(open_bound=...) must be bool")
		self.__open = open_bound
	
	def __new__(cls, *args, **kwargs):
		return super().__new__(cls, args[0])
	
	@property
	def open(self):
		return self.__open
	
	def __eq__(self, other):
		return math.isclose(self, other)


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
	def empty(cls, at: float = 0.0):
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
			raise TypeError(f"Type of argument(s) incorrect:  {self.__class__.__qualname__}({lower_bound}: float, {upper_bound}: float, {lower_bound_closed}: bool, {upper_bound_closed}: bool, {snap_infinitesimal}: bool)")
	
		self.__is_infinitesimal = False
		self.__is_degenerate = False
		self.__lower_bound = float(lower_bound)
		self.__upper_bound = float(upper_bound)
		self.__lower_bound_closed = bool(lower_bound_closed)
		self.__upper_bound_closed = bool(upper_bound_closed)
		
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
	def start(self):
		return self.__lower_bound
	
	@property
	def end(self):
		return self.__upper_bound
	
	@property
	def lower_bound(self):
		return self.__lower_bound
	
	@property
	def upper_bound(self):
		return self.__upper_bound
	
	@property
	def lower_bound_closed(self):
		return self.__lower_bound_closed
	
	@property
	def upper_bound_closed(self):
		return self.__upper_bound_closed
	
	@property
	def is_degenerate(self):
		return self.__is_degenerate
	
	@property
	def is_infinitesimal(self):
		return self.__is_infinitesimal
	
	@ property
	def length(self):
		return self.__upper_bound - self.__lower_bound
	
	def left_exterior(self):
		if self.__lower_bound == -Infinity:
			if self.__lower_bound_closed:
				return None
			else:
				return iInterval.empty(-Infinity)
		else:
			return iInterval(-Infinity, self.__lower_bound, lower_bound_closed=not self.__lower_bound_closed)
	
	def right_exterior(self):
		if self.__upper_bound == Infinity:
			if self.__upper_bound_closed:
				return None
			else:
				return iInterval.empty(Infinity)
		else:
			return iInterval(self.__upper_bound, Infinity, upper_bound_closed=not self.__upper_bound_closed)
		
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
	
	def intersect(self):
		pass