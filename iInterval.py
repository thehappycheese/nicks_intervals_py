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

from .Linked_iBound import Linked_iBound
from .iBound import PART_OF_LEFT
from .iBound import PART_OF_RIGHT
from .iBound import iBound
from .iBound import iBound_Negative_Infinity
from .iBound import iBound_Positive_Infinity

import NicksIntervals.iMulti_iInterval
from .non_atomic_super import non_atomic_super


class iInterval(non_atomic_super):
	"""Immutable Interval based on python's built in floats. Nothing fancy."""
	
	@classmethod
	def complete(cls):
		"""returns an interval spaning the complete real number line. Or at least all representable python floats."""
		return iInterval(lower_bound=iBound_Negative_Infinity, upper_bound=iBound_Positive_Infinity)
	
	@classmethod
	def inf(cls):
		"""Alias of .complete()"""
		return iInterval(iBound_Negative_Infinity, iBound_Positive_Infinity)

	@classmethod
	def degenerate(cls, value: float = 0.0):
		"""returns a zero-length 'degenerate' interval"""
		return iInterval(iBound(value, PART_OF_RIGHT), iBound(value, PART_OF_LEFT))
	
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
	
	@classmethod
	def inf_open(cls, upper_bound: float):
		return iInterval(iBound_Negative_Infinity, iBound(upper_bound, PART_OF_RIGHT))
	
	@classmethod
	def open_inf(cls, lower_bound: float):
		return iInterval(iBound(lower_bound, PART_OF_LEFT), iBound_Positive_Infinity)
	
	@classmethod
	def closed_inf(cls, lower_bound: float):
		return iInterval(iBound(lower_bound, PART_OF_RIGHT), iBound_Positive_Infinity)
	
	@classmethod
	def inf_closed(cls, upper_bound: float):
		return iInterval(iBound_Negative_Infinity, iBound(upper_bound, PART_OF_LEFT))
	
	@classmethod
	def empty(cls):
		"""returns a null or non-interval which is still of the type Iterable[iInterval] but will yield no items"""
		return NicksIntervals.iMulti_iInterval.iMulti_iInterval([])
	
	def __init__(self, lower_bound: iBound, upper_bound: iBound):
		if not (isinstance(lower_bound, iBound) and isinstance(upper_bound, iBound)):
			raise TypeError("Bounds must be an instance of iBound")
		
		self.__lower_bound: iBound = lower_bound
		self.__upper_bound: iBound = upper_bound
		
		self.__is_infinitesimal: bool = False
		self.__is_degenerate: bool = False
		
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
	
	def __bool__(self):
		return True
	
	def print(self):
		"""
		prints intervals and multi intervals like this for debugging (only works for integer intervals):
		╠═════╣
			╠═════╣    ╞═══╣
		"""
		lbv = round(self.__lower_bound.value) if math.isfinite(self.__lower_bound.value) else (-999 if self.__lower_bound.value == float('-inf') else 999)
		ubv = round(self.__upper_bound.value) if math.isfinite(self.__upper_bound.value) else (-999 if self.__upper_bound.value == float('-inf') else 999)
		out = f"{self:2.0f} :"
		for i in range(0, min(50, ubv) + 1):
			if i < lbv:
				out += " "
			elif lbv == i == ubv:
				out += "║"
			elif i == lbv:
				if self.__lower_bound.part_of_right:
					out += "╠"
				else:
					out += "╞"
			elif i == ubv:
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
	
	def get_linked_bounds(self) -> Tuple[Linked_iBound, Linked_iBound]:
		return (
			self.__lower_bound.get_Linked_iBound(linked_interval=self, is_lower_bound=True),
			self.__upper_bound.get_Linked_iBound(linked_interval=self, is_lower_bound=False)
		)
	
	def get_linked_interval(self):
		# TODO: linked interval?
		pass
	
	@property
	def is_degenerate(self) -> bool:
		return self.__is_degenerate
	
	@property
	def is_infinitesimal(self) -> bool:
		return self.__is_infinitesimal
	
	@property
	def is_complete(self) -> bool:
		return self.__lower_bound.value == float('-inf') and self.__upper_bound.value == float('inf')
	
	@ property
	def length(self) -> float:
		return self.__upper_bound.value - self.__lower_bound.value
	
	def interpolate(self, ratio: float) -> float:
		return self.__lower_bound.value + (self.__upper_bound.value - self.__lower_bound.value) * ratio
