"""
Nicholas Archer
2020/06/09

Roads are made of segments, and I nearly exploded with frustration writing code to work with overlapping or touching intervals.
"""

from __future__ import annotations

import itertools
import math
from typing import Iterable, Union, List, Any


class iBound (float):
	def __init__(self, value:float, open_bound:bool=False):
		if not isinstance(value, float):
			raise TypeError("iBound(value=...) must be float")
		if not isinstance(open_bound, bool):
			raise TypeError("iBound(open_bound=...) must be bool")
		assert (isinstance(value, bool))
		super().__init__(value)
		self.__open = open_bound
	@property
	def open(self):
		return self.__open


class iInterval:
	"""Immutable Interval based on python's built in floats. Nothing fancy."""
	def __init__(self, lower_bound: iBound, upper_bound: iBound):
		assert(isinstance(lower_bound, iBound))
		assert(isinstance(upper_bound, iBound))
		assert(lower_bound == upper_bound or lower_bound < upper_bound)
		self.__lower_bound = lower_bound
		self.__upper_bound = upper_bound
	
	@classmethod
	def complete(cls):
		return iInterval(iBound(0), iBound(0))